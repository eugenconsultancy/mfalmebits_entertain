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


# ─────────────────────────────────────────────────────────────────────
# 1. PHONE SANITIZATION — STRICT FOR PRODUCTION
# ─────────────────────────────────────────────────────────────────────
def _sanitize_phone(phone: str) -> str:
    """
    Normalise a Kenyan phone number to the 2547XXXXXXXX format required
    by the Daraja API.

    Strict rules for production:
        - Removes all non-digit characters
        - Converts 07... to 2547...
        - Converts 01... to 2541...
        - Ensures format starts with 254
        - Validates exactly 12 digits (254 + 9 digits)

    Accepts:  0712345678 | +254712345678 | 254712345678 | 712345678
    Returns:  254712345678
    Raises:   ValueError on unrecognisable formats.
    """
    # Remove all non-digit characters
    clean_phone = re.sub(r'\D', '', str(phone))
    
    # Remove leading '0' (e.g., 0712345678 -> 712345678)
    if clean_phone.startswith('0'):
        clean_phone = '254' + clean_phone[1:]
    
    # Remove leading '+' if present (already handled by regex)
    # Ensure it starts with 254
    if not clean_phone.startswith('254'):
        # Handle 7XXXXXX format (7 followed by 8 digits)
        if clean_phone.startswith('7') and len(clean_phone) == 9:
            clean_phone = '254' + clean_phone
        # Handle 1XXXXXX format (1 followed by 8 digits for landline)
        elif clean_phone.startswith('1') and len(clean_phone) == 9:
            clean_phone = '254' + clean_phone
        else:
            clean_phone = '254' + clean_phone
    
    # Final validation: must be exactly 12 digits (254 + 9 digits)
    if not re.fullmatch(r"254[17]\d{8}", clean_phone):
        raise ValueError(
            f"Invalid Kenyan phone number: '{phone}'. "
            "Expected format: 254712345678 (12 digits starting with 2547 or 2541)"
        )
    
    return clean_phone


# ─────────────────────────────────────────────────────────────────────
# 2. DYNAMIC CALLBACK URL LOGIC — AUTOMATIC DOMAIN HANDLING
# ─────────────────────────────────────────────────────────────────────
def _get_callback_url() -> str:
    """
    Determine the correct callback URL based on environment.
    
    - If in sandbox with ngrok, returns the configured ngrok URL.
    - If in production, automatically enforces HTTPS and uses production domain.
    - Falls back to settings.MPESA_CALLBACK_URL.
    """
    callback_url = getattr(settings, "MPESA_CALLBACK_URL", "")
    environment = getattr(settings, "MPESA_ENVIRONMENT", "sandbox").lower()
    
    # If using ngrok in production (should not happen), force production URL
    if "ngrok" in callback_url and environment == "production":
        logger.warning(
            "ngrok URL detected in production environment. "
            "Overriding with production domain: https://mfalmebits.africa/payments/callback/"
        )
        return "https://mfalmebits.africa/api/mpesa/callback/"
    
    # Ensure HTTPS in production
    if environment == "production" and callback_url and not callback_url.startswith("https://"):
        logger.warning(
            f"Callback URL {callback_url} is not HTTPS. "
            "Enforcing HTTPS for production."
        )
        callback_url = callback_url.replace("http://", "https://")
    
    return callback_url


# ─────────────────────────────────────────────────────────────────────
# 3. ACCESS TOKEN WITH RETRY AND TIMEOUT
# ─────────────────────────────────────────────────────────────────────
def get_access_token(retry_count: int = 2) -> str | None:
    """
    Generate a Bearer access token from Safaricom's OAuth endpoint.
    Tokens are valid for 3 600 seconds (1 hour).

    Args:
        retry_count: Number of retry attempts on failure.

    Returns:
        str: The raw access_token string, or None on failure.

    Raises:
        RuntimeError: When configuration is missing.
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

    for attempt in range(retry_count + 1):
        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Basic {credentials}"},
                timeout=15,  # Timeout for VPS stability
            )
            response.raise_for_status()
            data = response.json()

            token = data.get("access_token")
            if not token:
                logger.error(f"Unexpected OAuth response: {data}")
                continue

            logger.info("M-Pesa access token obtained successfully.")
            return token

        except requests.exceptions.Timeout:
            logger.warning(f"M-Pesa OAuth endpoint timed out (attempt {attempt + 1}/{retry_count + 1})")
            if attempt == retry_count:
                logger.error("M-Pesa OAuth endpoint timed out after all retries.")
                return None
        except requests.exceptions.ConnectionError as exc:
            logger.warning(f"Could not reach M-Pesa API (attempt {attempt + 1}/{retry_count + 1}): {exc}")
            if attempt == retry_count:
                logger.error("M-Pesa OAuth connection failed after all retries.")
                return None
        except requests.exceptions.HTTPError as exc:
            logger.error(
                f"M-Pesa OAuth failed [{response.status_code}]: {response.text}"
            )
            return None
        except Exception as exc:
            logger.exception(f"Unexpected M-Pesa OAuth error: {exc}")
            return None

    return None


def _get_cached_token() -> str | None:
    """
    Wrapper that caches the access token in Django's cache backend for
    55 minutes (token TTL is 60 min; we refresh 5 min early).
    """
    from django.core.cache import cache

    token = cache.get("mpesa_access_token")
    if not token:
        token = get_access_token()
        if token:
            cache.set("mpesa_access_token", token, timeout=55 * 60)  # 55 min
        else:
            logger.error("Failed to obtain M-Pesa access token")
    return token


# ─────────────────────────────────────────────────────────────────────
# 4. PASSWORD / TIMESTAMP GENERATION
# ─────────────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────────────
# 5. STK PUSH (EXPRESS CHECKOUT)
# ─────────────────────────────────────────────────────────────────────
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
    try:
        phone = _sanitize_phone(phone_number)
    except ValueError as e:
        return {"success": False, "error": str(e), "status_code": 400}

    amount = int(amount)  # M-Pesa requires whole KES amounts

    shortcode = str(getattr(settings, "MPESA_SHORTCODE", ""))
    _callback = callback_url or _get_callback_url()

    if not _callback:
        raise RuntimeError(
            "MPESA_CALLBACK_URL must be set in settings or passed explicitly."
        )
    
    # Ensure HTTPS for production callback
    environment = getattr(settings, "MPESA_ENVIRONMENT", "sandbox").lower()
    if environment == "production" and not _callback.startswith("https://"):
        raise RuntimeError(
            f"MPESA_CALLBACK_URL must be a public HTTPS URL in production. "
            f"Got: {_callback!r}"
        )

    # Get access token with retry
    token = _get_cached_token()
    if not token:
        return {
            "success": False,
            "error": "Unable to obtain M-Pesa access token. Please try again later.",
            "status_code": 503,
        }

    password, timestamp = _generate_password()

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
        return {"success": False, "error": "Request timed out. Please try again.", "status_code": 504}
    except requests.exceptions.ConnectionError as exc:
        logger.error("STK Push connection error: %s", exc)
        return {"success": False, "error": "Could not reach M-Pesa API.", "status_code": 503}
    except Exception as exc:
        logger.exception("Unexpected STK Push error: %s", exc)
        return {"success": False, "error": str(exc), "status_code": 500}


# ─────────────────────────────────────────────────────────────────────
# 6. STK QUERY (CHECK TRANSACTION STATUS)
# ─────────────────────────────────────────────────────────────────────
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
    
    # Get access token with retry
    token = _get_cached_token()
    if not token:
        return {
            "success": False,
            "ResultCode": "-1",
            "ResultDesc": "Unable to obtain M-Pesa access token",
        }
    
    password, timestamp = _generate_password()

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
    except Exception as exc:
        logger.exception("STK Query failed: %s", exc)
        return {"success": False, "ResultCode": "-1", "ResultDesc": str(exc)}


# ─────────────────────────────────────────────────────────────────────
# 7. CALLBACK HANDLER (PARSE SAFARICOM RESPONSE)
# ─────────────────────────────────────────────────────────────────────
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
        callback_metadata = stk_callback.get("CallbackMetadata")
        if not callback_metadata:
            logger.warning("Payment succeeded but no CallbackMetadata received")
            return {
                "success": True,
                "result_code": result_code,
                "result_desc": result_desc,
                "checkout_request_id": checkout_request_id,
                "merchant_request_id": merchant_request_id,
                "amount": None,
                "phone": None,
                "receipt_number": None,
                "transaction_date": None,
            }

        items = {
            item["Name"]: item.get("Value")
            for item in callback_metadata.get("Item", [])
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
    except Exception as exc:
        logger.exception("Unexpected error parsing M-Pesa callback: %s", exc)
        return {
            "success": False,
            "result_code": -1,
            "result_desc": str(exc),
        }