from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from djbcknd.models import Profile


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get('access_token')

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)

        # 🆕 Presence update — runs AFTER successful JWT validation
        if user is not None:
            try:
                now = timezone.now()
                profile = Profile.objects.only('last_seen_at').get(user_id=user.id)
                if (
                    profile.last_seen_at is None
                    or (now - profile.last_seen_at).total_seconds() >= 30
                ):
                    Profile.objects.filter(user_id=user.id).update(last_seen_at=now)
            except Profile.DoesNotExist:
                pass
            except Exception:
                pass  # presence is non-critical, never break auth

        return user, validated_token