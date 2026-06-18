import ipaddress

from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class VersionedJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        token_version = int(validated_token.get('auth_version', 0))
        if token_version != user.auth_version:
            raise AuthenticationFailed(
                'Session has been revoked.',
                code='session_revoked',
            )
        return user

    def authenticate(self, request):
        authenticated = super().authenticate(request)
        if authenticated is None:
            return None
        user, validated_token = authenticated
        password_change_path = request.path.endswith('/auth/change-password/')
        if (
            not password_change_path
            and user.company_memberships.filter(
                is_active=True,
                force_password_change=True,
            ).exists()
        ):
            raise AuthenticationFailed(
                'Password change is required.',
                code='password_change_required',
            )
        self._record_session(request, user, validated_token)
        return authenticated

    @staticmethod
    def _record_session(request, user, validated_token):
        from teams.models import TeamSession

        token_jti = str(validated_token.get('jti', ''))
        if not token_jti:
            return
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
        ip_address = (
            forwarded.split(',')[0].strip()
            if forwarded
            else request.META.get('REMOTE_ADDR')
        )
        try:
            ip_address = str(ipaddress.ip_address(ip_address)) if ip_address else None
        except ValueError:
            ip_address = None
        browser = user_agent.split(' ')[-1][:255] if user_agent else 'Unknown'
        TeamSession.objects.update_or_create(
            token_jti=token_jti,
            defaults={
                'user': user,
                'device': user_agent or 'Unknown device',
                'browser': browser,
                'ip_address': ip_address or None,
                'revoked_at': None,
                'last_active_at': timezone.now(),
            },
        )
