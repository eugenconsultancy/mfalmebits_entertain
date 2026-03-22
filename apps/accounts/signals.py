from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, UserPreference


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create profile when user is created - ONLY on creation"""
    if created:
        Profile.objects.get_or_create(user=instance)
        print(f"✅ Profile created for user: {instance.username}")


@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    """Create preferences when user is created - ONLY on creation"""
    if created:
        UserPreference.objects.get_or_create(user=instance)
        print(f"✅ Preferences created for user: {instance.username}")


# REMOVED: save_user_profile signal - was causing integrity errors
# The signal below is removed because it saves the profile on EVERY User save,
# which can cause integrity issues when the profile doesn't exist yet.
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     """Save profile when user is saved"""
#     if hasattr(instance, 'profile'):
#         instance.profile.save()