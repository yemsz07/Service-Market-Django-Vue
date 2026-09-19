from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .profile import Profile


# ==========================================
# 🔔 5. SIGNALS (Automatic Profile Generator)
# ==========================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically creates a matching Profile instance whenever a new User registers.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Ensures existing Profile updates cleanly when the User instance is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()