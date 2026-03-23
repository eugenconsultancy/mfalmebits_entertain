"""
Signals for accounts app
IMPORTANT: All signals are now defined in models.py to prevent duplication
This file is kept for reference but signals are imported from models.py
"""

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

# Note: The actual signals are defined in models.py
# This file is kept for documentation purposes only.
# To use signals, import them from models.py or define them here.

# If you need to add additional signals, add them here:
# @receiver(post_save, sender=User)
# def additional_user_signal(sender, instance, created, **kwargs):
#     """Additional signal handler"""
#     pass