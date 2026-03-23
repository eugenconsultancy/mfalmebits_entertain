"""
Create admin superuser script - Fixed for Render deployment
Place this file in your project root directory
"""
import os
import sys
import django

# Set Django settings module to render settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.render')

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize Django
django.setup()

def create_superuser():
    """
    Create or update superuser without causing login loops
    """
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import User as AuthUser
    
    User = get_user_model()
    
    # Get credentials from environment variables
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'culture')
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'culture@gmail.com')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD', '64006400')
    
    print(f"🔍 Checking for superuser: {username}")
    
    try:
        # Try to get existing user
        user = User.objects.get(username=username)
        
        # Check if user has proper superuser flags
        needs_update = False
        
        if not user.is_superuser:
            user.is_superuser = True
            needs_update = True
            print(f"   Upgrading user to superuser")
            
        if not user.is_staff:
            user.is_staff = True
            needs_update = True
            print(f"   Upgrading user to staff")
        
        # Only set password if it's not usable or explicitly needed
        if not user.has_usable_password():
            user.set_password(password)
            needs_update = True
            print(f"   Setting password (was unusable)")
        
        if needs_update:
            user.save()
            print(f"✅ Updated existing user '{username}'")
        else:
            print(f"✅ Superuser '{username}' already exists with valid credentials")
        
        print(f"   Login URL: https://mfalmebits-entertain.onrender.com/admin/")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        
    except User.DoesNotExist:
        # Create new superuser
        print(f"📝 Creating new superuser: {username}")
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✅ Superuser '{username}' created successfully")
    
    # Verify the user
    user = User.objects.get(username=username)
    if user.is_superuser and user.is_staff and user.has_usable_password():
        print(f"🎉 Superuser verification PASSED")
        return True
    else:
        print(f"⚠️ Superuser verification FAILED")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MfalmeBits Entertainment - Superuser Setup")
    print("=" * 60)
    
    success = create_superuser()
    
    if success:
        print("=" * 60)
        print("✅ Superuser setup completed successfully")
        print("=" * 60)
        sys.exit(0)
    else:
        print("=" * 60)
        print("❌ Superuser setup failed - check logs above")
        print("=" * 60)
        sys.exit(1)