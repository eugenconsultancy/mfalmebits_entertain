"""
Create admin superuser script - Fixed for Render deployment
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
            print(f"   ✓ Upgrading user to superuser")
            
        if not user.is_staff:
            user.is_staff = True
            needs_update = True
            print(f"   ✓ Upgrading user to staff")
        
        # Only set password if it's not usable
        if not user.has_usable_password():
            user.set_password(password)
            needs_update = True
            print(f"   ✓ Setting password (was unusable)")
        
        if needs_update:
            user.save()
            print(f"✅ Updated existing user '{username}'")
        else:
            print(f"✅ Superuser '{username}' already exists with valid credentials")
        
        print(f"\n📋 Login Information:")
        print(f"   URL: https://mfalmebits-entertain.onrender.com/admin/")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {'*' * len(password)} (hidden)")
        
        return True
        
    except User.DoesNotExist:
        # Create new superuser
        print(f"📝 Creating new superuser: {username}")
        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            print(f"✅ Superuser '{username}' created successfully")
            return True
        except Exception as e:
            print(f"❌ Error creating superuser: {str(e)}")
            return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("MfalmeBits Entertainment - Superuser Setup")
    print("=" * 60)
    
    success = create_superuser()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Superuser setup completed successfully")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Superuser setup failed - check logs above")
        print("=" * 60)
        sys.exit(1)