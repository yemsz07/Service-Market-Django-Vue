from django.utils import timezone
from datetime import timedelta
from djbcknd.models import Profile


ONLINE_WINDOW = timedelta(seconds=120)   # 2 min idle = offline
UPDATE_THROTTLE = 30                     # update every 30s lang


def is_user_online(user_id):
    """Quick check — 1 query. Fallback sa False kung walang record."""
    try:
        last_seen = Profile.objects.values_list('last_seen_at', flat=True).get(user_id=user_id)
    except Profile.DoesNotExist:
        return False
    if last_seen is None:
        return False
    return timezone.now() - last_seen < ONLINE_WINDOW


def mark_user_online(user_id):
    """Update last_seen_at, throttled para hindi mag-spam sa DB."""
    now = timezone.now()
    try:
        profile = Profile.objects.only('last_seen_at').get(user_id=user_id)
    except Profile.DoesNotExist:
        return   # walang profile — silent fail

    if profile.last_seen_at and (now - profile.last_seen_at).total_seconds() < UPDATE_THROTTLE:
        return   # nag-update na recently

    Profile.objects.filter(user_id=user_id).update(last_seen_at=now)