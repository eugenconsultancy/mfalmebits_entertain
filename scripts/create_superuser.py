#!/usr/bin/env python
"""
Create superuser script for MfalmeBits
Run during deployment to ensure admin user exists
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.render')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_superuser():
    """Create superuser if it doesn't exist"""
    
    # Check if superuser exists
    if User.objects.filter(is_superuser=True).exists():
        print("✅ Superuser already exists")
        return True
    
    # Get credentials from environment
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@mfalmebits.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', None)
    
    # Validate password
    if not password:
        print("❌ ERROR: DJANGO_SUPERUSER_PASSWORD environment variable not set!")
        print("   Please add this variable in your Render dashboard")
        return False
    
    # Create superuser
    try:
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✅ Superuser created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        return True
    except Exception as e:
        print(f"❌ Failed to create superuser: {e}")
        return False

if __name__ == "__main__":
    success = create_superuser()
    sys.exit(0 if success else 1)
