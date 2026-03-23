"""
Create admin superuser script - SAFE version that never overwrites passwords
"""
import os
import sys
import django

# Ensure Django is initialized with production settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.render')

# Add project root to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

django.setup()

def create_culture_admin():
    """
    Create or update the culture superuser WITHOUT overwriting existing passwords.
    This is critical for Render free tier where the script runs on every deploy.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Get credentials from environment variables (set in Render dashboard)
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'culture')
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'culture@gmail.com')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD', '64006400')
    
    print(f"🔍 Checking for superuser: {username}")
    
    try:
        # Try to get existing user
        user = User.objects.get(username=username)
        
        # User exists - check if password is usable
        if user.has_usable_password():
            print(f"✅ Superuser '{username}' already exists with valid password.")
            print(f"   Password NOT changed to preserve existing credentials.")
            print(f"   Use: {username} or {email} with your current password.")
        else:
            # Password is unusable (e.g., old hashing algorithm)
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print(f"🔑 Reset password for existing user '{username}' (password was unusable).")
        
    except User.DoesNotExist:
        # Create new superuser
        print(f"📝 Creating new superuser: {username}")
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✅ Superuser '{username}' created successfully.")
        print(f"   Login with username: {username} OR email: {email}")
    
    # Verify the user is properly configured
    user.refresh_from_db()
    if user.is_superuser and user.is_staff and user.has_usable_password():
        print(f"🎉 Superuser verification PASSED")
        return True
    else:
        print(f"⚠️  Superuser verification FAILED - check user flags")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("MfalmeBits Superuser Setup")
    print("=" * 50)
    
    success = create_culture_admin()
    
    if success:
        print("=" * 50)
        print("✅ Superuser setup complete")
        print("=" * 50)
        sys.exit(0)
    else:
        print("=" * 50)
        print("❌ Superuser setup failed")
        print("=" * 50)
        sys.exit(1)