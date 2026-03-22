# MfalmeBits - African Knowledge Archive & Digital Library

## 🚀 Project Overview
MfalmeBits is a comprehensive Django-based platform for African knowledge archive, digital library, and cultural preservation.

## 📋 Features
- Glassmorphism UI with smooth animations
- SEO-optimized architecture
- Knowledge Archive with themes
- Digital Library/Store
- Institutional licensing
- Co-brand collaborations
- Blog/News section
- Newsletter management
- User authentication

## 🛠️ Tech Stack
- Django 4.2.7
- PostgreSQL (production) / SQLite (development)
- Redis for caching
- Celery for background tasks
- Elasticsearch for search
- Stripe/PayPal for payments
- Bootstrap 5 for styling

## 🏗️ Project Structure
mfalme_entertain/
├── apps/ # Django applications
├── core/ # Project configuration
├── static/ # Static files
├── media/ # User uploads
├── templates/ # HTML templates
├── utils/ # Helper functions
└── requirements.txt

text

## 🚦 Quick Start

1. Clone the repository
```bash
git clone https://github.com/yourusername/mfalme_entertain.git
cd mfalme_entertain
Create virtual environment

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
Install dependencies

bash
pip install -r requirements.txt
Configure environment

bash
cp .env.example .env
# Edit .env with your settings
Run migrations

bash
python manage.py migrate
Create superuser

bash
python manage.py createsuperuser
Run development server

bash
python manage.py runserver
🔧 Environment Variables
DJANGO_SECRET_KEY: Django secret key

DATABASE_URL: Database connection string

STRIPE_*: Stripe API keys

EMAIL_*: Email configuration

AWS_*: AWS S3 configuration (production)

📊 SEO Features
XML Sitemaps

robots.txt

Canonical URLs

Meta tags generator

Schema.org structured data

SEO-friendly URLs

Image optimization

Breadcrumbs

Pagination with rel=prev/next

404 page optimization

🎨 UI/UX
Glassmorphism design

Smooth animations

Parallax scrolling

Magnetic buttons

Lazy loading

Responsive design

📈 Performance
Image optimization

Caching strategies

Database query optimization

CDN ready

Gzip compression

Minified assets

🔒 Security
HTTPS enforcement

CSRF protection

XSS prevention

SQL injection protection

Rate limiting

Secure file uploads

📝 License
Copyright © 2024 MfalmeBits. All rights reserved.

🤝 Contributing
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

📞 Contact
Website: https://mfalmebits.com

Email: info@mfalmebits.com

Twitter: @mfalmebits
EOF

text

### **Step 21: Initial Git Commit**

```bash
# Add all files
git add .

# Initial commit
git commit -m "Initial commit: MfalmeBits Django project with SEO optimization"

# Create main branch
git branch -M main

# Add remote (replace with your repo URL)
# git remote add origin https://github.com/yourusername/mfalme_entertain.git

# Push to remote
# git push -u origin main




To move **MfalmeBits** from a local development environment to a professional, production-ready "Digital Sanctuary," you need to configure these services one by one.

Here is your step-by-step technical guide for each component.

---

## 1. Stripe (Payments for the Library)

This allows you to sell the **5K+ Digital Products** mentioned in your "About Us" section.

1. **Create Account:** Go to [Stripe.com](https://stripe.com) and register.
2. **Get API Keys:** Navigate to **Developers > API Keys**.
* Copy the **Publishable key** (`pk_test_...`) and **Secret key** (`sk_test_...`).


3. **Configure Webhooks:** Since your backend needs to know when a payment is finished:
* Go to **Developers > Webhooks**.
* Add an endpoint: `https://yourdomain.com/stripe/webhook/`.
* Select the event: `checkout.session.completed`.
* Copy the **Signing Secret** (`whsec_...`).


4. **Update `.env`:**
```env
STRIPE_PUBLIC_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_secret

```



---

## 2. AWS S3 (Storage for 10K+ Archive Entries)

Standard web hosting is too slow and small for 10,000+ high-resolution cultural artifacts. S3 provides professional-grade storage.

1. **Create Bucket:** In the [AWS Console](https://console.aws.amazon.com/s3/), create a bucket named `mfalmebits-media`.
* **Uncheck** "Block all public access" (since your blog images need to be visible to the world).


2. **IAM User:** Go to **IAM > Users** and create a user named `django-mfalme-user`.
* Attach the policy: `AmazonS3FullAccess`.
* Go to **Security Credentials** and "Create Access Key".


3. **Save Credentials:** Download the `.csv` with your `Access Key ID` and `Secret Access Key`.
4. **Update Django `production.py`:**
```python
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'mfalmebits-media'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

```



---

## 3. Postmark/SendGrid (Mandatory Email Verification)

You have `ACCOUNT_EMAIL_VERIFICATION = 'mandatory'` in your settings. If this isn't configured, new users cannot join your **50K+ Community**.

1. **Sign Up:** Create an account at [Postmark](https://postmarkapp.com/).
2. **Verify Domain:** You must add DNS records (DKIM and Return-Path) to your domain provider (e.g., Namecheap or GoDaddy) to prove you own `mfalmebits.com`.
3. **Get Server Token:** Create a "Server" in Postmark and copy the **API Token**.
4. **Update `.env`:**
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.postmarkapp.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-postmark-token
EMAIL_HOST_PASSWORD=your-postmark-token
EMAIL_USE_TLS=True

```



---

## 4. Google Social Auth (Community Login)

This allows users to "Join Our Mission" with one click.

1. **Cloud Console:** Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. **Create Project:** Named "MfalmeBits-Auth".
3. **OAuth Consent Screen:** Set to "External" and add your logo and support email.
4. **Credentials:** Create **OAuth 2.0 Client IDs**.
* **Authorized Redirect URI:** `https://mfalmebits.com/accounts/google/login/callback/`.


5. **Django Admin Setup:**
* Go to `127.0.0.1:8000/admin`.
* Under **Social Accounts > Social Applications**, add "Google".
* Paste the **Client ID** and **Secret Key**.



---

## 5. Redis & Celery (Background Tasks)

You have `django_celery_beat` in your settings. This is needed for sending the **Newsletter** and cleaning up the **Archive** without slowing down the site.

1. **Install Redis:** On your server (or via Docker), ensure Redis is running.
2. **Configure Celery:** Create a `celery.py` file next to your `settings.py`.
3. **Update `.env`:**
```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

```



---

### Pro-Tip for your Nairobi Deployment

Since you are based in **Nairobi (Africa/Nairobi)**, ensure your server time matches. You already have `TIME_ZONE = 'Africa/Nairobi'` in your `base.py`, which is perfect. This ensures that when a researcher uploads an entry to the archive, the "Date Added" is accurate to Kenyan time.

**Which of these would you like to tackle first? I can provide the specific code snippets for your `production.py` to make the AWS or Stripe integration live.**



































Internal Database URL; postgresql://mfalme_bits_db_user:GY10riZX8oBihwZ1nqwTOKgxz50knUyT@dpg-d7005q24d50c73911djg-a/mfalme_bits_db
External Database URL: postgresql://mfalme_bits_db_user:GY10riZX8oBihwZ1nqwTOKgxz50knUyT@dpg-d7005q24d50c73911djg-a.singapore-postgres.render.com/mfalme_bits_db

Database;
mfalme_bits_db

Username;
mfalme_bits_db_user

Password; GY10riZX8oBihwZ1nqwTOKgxz50knUyT