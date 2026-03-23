import os
import django
from django.contrib.auth import get_user_model

# Ensure Django is initialized
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.render')
django.setup()

def create_culture_admin():
    User = get_user_model()
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'culture')
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'culture@gmail.com')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD', '64006400')

    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser: {username}...")
        User.objects.create_superuser(username=username, email=email, password=password)
        print("Superuser created successfully.")
    else:
        print(f"Superuser {username} already exists. Skipping.")

if __name__ == "__main__":
    create_culture_admin()