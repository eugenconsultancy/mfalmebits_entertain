"""
utils/payments.py
─────────────────────────────────────────────────────────────────────
M-Pesa Daraja API 3.0 — STK Push (Lipa Na M-Pesa Online)

Environment variables required (.env):
    MPESA_CONSUMER_KEY        - From Daraja app
    MPESA_CONSUMER_SECRET     - From Daraja app
    MPESA_PASSKEY             - Lipa Na M-Pesa Online Passkey
    MPESA_SHORTCODE           - Business shortcode (Paybill / Till)
    MPESA_CALLBACK_URL        - Public HTTPS URL for callback
    MPESA_ENVIRONMENT         - "sandbox" | "production"

Usage:
    from utils.payments import initiate_stk_push
    result = initiate_stk_push(
        phone_number="254712345678",
        amount=500,
        account_ref="ORDER-001",
        description="Purchase of eBook"
    )
"""

import base64
import logging
import re
from datetime import datetime

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# ── API base URLs ────────────────────────────────────────────────────
_SANDBOX_BASE = "https://sandbox.safaricom.co.ke"
_PRODUCTION_BASE = "https://api.safaricom.co.ke"


def _base_url() -> str:
    """Return the correct API base URL based on MPESA_ENVIRONMENT."""
    env = getattr(settings, "MPESA_ENVIRONMENT", "sandbox").lower()
    return _PRODUCTION_BASE if env == "production" else _SANDBOX_BASE


def _sanitize_phone(phone: str) -> str:
    """
    Normalise a Kenyan phone number to the 2547XXXXXXXX format required
    by the Daraja API.

    Accepts:  0712345678 | +254712345678 | 254712345678 | 712345678
    Returns:  254712345678
    Raises:   ValueError on unrecognisable formats.
    """
    phone = re.sub(r"[\s\-\(\)]", "", str(phone))

    if phone.startswith("+"):
        phone = phone[1:]

    if phone.startswith("0"):
        phone = "254" + phone[1:]

    if phone.startswith("7") and len(phone) == 9:
        phone = "254" + phone

    if not re.fullmatch(r"2547\d{8}", phone):
        raise ValueError(
            f"Invalid Kenyan phone number: '{phone}'. "
            "Expected format: 254712345678"
        )

    return phone


# ── 1. Access Token ──────────────────────────────────────────────────

def get_access_token() -> str:
    """
    Generate a Bearer access token from Safaricom's OAuth endpoint.

    Tokens are valid for 3 600 seconds (1 hour).  In production you
    should cache this value (e.g. in Django's cache framework) and only
    refresh it when expired.

    Returns:
        str: The raw access_token string.

    Raises:
        RuntimeError: When the API request fails or credentials are wrong.
    """
    consumer_key = getattr(settings, "MPESA_CONSUMER_KEY", "")
    consumer_secret = getattr(settings, "MPESA_CONSUMER_SECRET", "")

    if not consumer_key or not consumer_secret:
        raise RuntimeError(
            "MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET must be set "
            "in your Django settings / environment variables."
        )

    url = f"{_base_url()}/oauth/v1/generate?grant_type=client_credentials"
    credentials = base64.b64encode(
        f"{consumer_key}:{consumer_secret}".encode()
    ).decode("utf-8")

    try:
        response = requests.get(
            url,
            headers={"Authorization": f"Basic {credentials}"},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        token = data.get("access_token")
        if not token:
            raise RuntimeError(f"Unexpected OAuth response: {data}")

        logger.info("M-Pesa access token obtained successfully.")
        return token

    except requests.exceptions.Timeout:
        raise RuntimeError("M-Pesa OAuth endpoint timed out.")
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(f"Could not reach M-Pesa API: {exc}")
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(
            f"M-Pesa OAuth failed [{response.status_code}]: "
            f"{response.text}"
        ) from exc


def _get_cached_token() -> str:
    """
    Wrapper that caches the access token in Django's cache backend for
    55 minutes (token TTL is 60 min; we refresh 5 min early).
    """
    from django.core.cache import cache

    token = cache.get("mpesa_access_token")
    if not token:
        token = get_access_token()
        cache.set("mpesa_access_token", token, timeout=55 * 60)  # 55 min
    return token


# ── 2. Password / Timestamp ──────────────────────────────────────────

def _generate_password() -> tuple[str, str]:
    """
    Generate the Base64-encoded password and timestamp required by the
    STK Push endpoint.

    Formula:  Base64(Shortcode + Passkey + Timestamp)
    Timestamp format: YYYYMMDDHHmmss

    Returns:
        (password, timestamp) — both as strings.
    """
    shortcode = str(getattr(settings, "MPESA_SHORTCODE", ""))
    passkey = getattr(settings, "MPESA_PASSKEY", "")

    if not shortcode or not passkey:
        raise RuntimeError(
            "MPESA_SHORTCODE and MPESA_PASSKEY must be set in settings."
        )

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    raw = f"{shortcode}{passkey}{timestamp}"
    password = base64.b64encode(raw.encode()).decode("utf-8")
    return password, timestamp


# ── 3. STK Push (Express Checkout) ──────────────────────────────────

def initiate_stk_push(
    phone_number: str,
    amount: int | float,
    account_ref: str = "MfalmeBits",
    description: str = "Payment",
    callback_url: str | None = None,
) -> dict:
    """
    Initiate a Lipa Na M-Pesa Online (STK Push) payment request.

    The customer receives a PIN prompt on their phone; they confirm and
    Safaricom sends the result to `callback_url`.

    Args:
        phone_number:  Kenyan mobile number in any common format.
        amount:        Amount in KES (whole number; fractions are truncated).
        account_ref:   Account reference shown on the customer's receipt.
        description:   Short description of the transaction (≤13 chars).
        callback_url:  Override the default MPESA_CALLBACK_URL setting.

    Returns:
        dict with keys:
            success (bool)
            MerchantRequestID, CheckoutRequestID, ResponseDescription
                — on success
            error (str), status_code (int)
                — on failure

    Raises:
        ValueError: For invalid phone numbers.
        RuntimeError: For missing configuration.
    """
    phone = _sanitize_phone(phone_number)
    amount = int(amount)  # M-Pesa requires whole KES amounts

    shortcode = str(getattr(settings, "MPESA_SHORTCODE", ""))
    _callback = callback_url or getattr(settings, "MPESA_CALLBACK_URL", "")

    if not _callback:
        raise RuntimeError(
            "MPESA_CALLBACK_URL must be set in settings or passed explicitly."
        )
    if not _callback.startswith("https://"):
        raise RuntimeError(
            "MPESA_CALLBACK_URL must be a public HTTPS URL. "
            f"Got: {_callback!r}"
        )

    password, timestamp = _generate_password()
    token = _get_cached_token()

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",  # Use "CustomerBuyGoodsOnline" for Till
        "Amount": amount,
        "PartyA": phone,
        "PartyB": shortcode,
        "PhoneNumber": phone,
        "CallBackURL": _callback,
        "AccountReference": account_ref[:12],   # Max 12 chars
        "TransactionDesc": description[:13],    # Max 13 chars
    }

    url = f"{_base_url()}/mpesa/stkpush/v1/processrequest"

    try:
        response = requests.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        data = response.json()
        logger.info("STK Push response: %s", data)

        # Safaricom returns ResponseCode "0" for a successfully queued request
        if response.status_code == 200 and data.get("ResponseCode") == "0":
            return {
                "success": True,
                "MerchantRequestID": data.get("MerchantRequestID"),
                "CheckoutRequestID": data.get("CheckoutRequestID"),
                "ResponseDescription": data.get("ResponseDescription"),
                "CustomerMessage": data.get("CustomerMessage"),
            }

        # Handle API-level errors (e.g. wrong credentials, bad amount)
        return {
            "success": False,
            "error": data.get("errorMessage") or data.get("ResponseDescription", "Unknown error"),
            "status_code": response.status_code,
            "raw": data,
        }

    except requests.exceptions.Timeout:
        logger.error("STK Push timed out for phone %s", phone)
        return {"success": False, "error": "Request timed out.", "status_code": 504}
    except requests.exceptions.ConnectionError as exc:
        logger.error("STK Push connection error: %s", exc)
        return {"success": False, "error": "Could not reach M-Pesa API.", "status_code": 503}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected STK Push error: %s", exc)
        return {"success": False, "error": str(exc), "status_code": 500}


# ── 4. STK Query (check transaction status) ─────────────────────────

def query_stk_push(checkout_request_id: str) -> dict:
    """
    Query the status of a previously initiated STK Push transaction.

    Useful when the callback has not arrived within your expected window.

    Args:
        checkout_request_id: The CheckoutRequestID from initiate_stk_push().

    Returns:
        dict with ResultCode (str), ResultDesc (str), and success (bool).
    """
    shortcode = str(getattr(settings, "MPESA_SHORTCODE", ""))
    password, timestamp = _generate_password()
    token = _get_cached_token()

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id,
    }

    url = f"{_base_url()}/mpesa/stkpushquery/v1/query"

    try:
        response = requests.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=20,
        )
        data = response.json()
        result_code = str(data.get("ResultCode", "-1"))

        return {
            "success": result_code == "0",
            "ResultCode": result_code,
            "ResultDesc": data.get("ResultDesc", ""),
            "raw": data,
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("STK Query failed: %s", exc)
        return {"success": False, "ResultCode": "-1", "ResultDesc": str(exc)}


# ── 5. Callback Handler (call from your Django view) ─────────────────

def parse_callback(request_body: dict) -> dict:
    """
    Parse the JSON body posted by Safaricom to your MPESA_CALLBACK_URL.

    Your callback view should be csrf_exempt and accept POST only:

        @csrf_exempt
        def mpesa_callback(request):
            import json
            data = json.loads(request.body)
            result = parse_callback(data)
            # Save result to your Purchase model here
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

    Args:
        request_body: Parsed JSON dict from request.body.

    Returns:
        dict with:
            success (bool)
            checkout_request_id, merchant_request_id
            amount, phone, receipt_number, transaction_date
                — on success
            result_code, result_desc
                — always present
    """
    try:
        stk_callback = request_body["Body"]["stkCallback"]

        result_code = int(stk_callback.get("ResultCode", -1))
        result_desc = stk_callback.get("ResultDesc", "")
        merchant_request_id = stk_callback.get("MerchantRequestID", "")
        checkout_request_id = stk_callback.get("CheckoutRequestID", "")

        if result_code != 0:
            logger.warning(
                "M-Pesa payment failed [%s]: %s | CheckoutReqID=%s",
                result_code, result_desc, checkout_request_id,
            )
            return {
                "success": False,
                "result_code": result_code,
                "result_desc": result_desc,
                "checkout_request_id": checkout_request_id,
                "merchant_request_id": merchant_request_id,
            }

        # Payment succeeded — extract metadata items
        items = {
            item["Name"]: item.get("Value")
            for item in stk_callback["CallbackMetadata"]["Item"]
        }

        amount = items.get("Amount")
        receipt_number = items.get("MpesaReceiptNumber")
        transaction_date = items.get("TransactionDate")
        phone = str(items.get("PhoneNumber", ""))

        logger.info(
            "M-Pesa payment confirmed: receipt=%s amount=%s phone=%s",
            receipt_number, amount, phone,
        )

        return {
            "success": True,
            "result_code": result_code,
            "result_desc": result_desc,
            "checkout_request_id": checkout_request_id,
            "merchant_request_id": merchant_request_id,
            "amount": amount,
            "phone": phone,
            "receipt_number": receipt_number,
            "transaction_date": transaction_date,
        }

    except KeyError as exc:
        logger.error("Malformed M-Pesa callback body (missing key %s): %s", exc, request_body)
        return {
            "success": False,
            "result_code": -1,
            "result_desc": f"Malformed callback: missing key {exc}",
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected error parsing M-Pesa callback: %s", exc)
        return {
            "success": False,
            "result_code": -1,
            "result_desc": str(exc),
        }