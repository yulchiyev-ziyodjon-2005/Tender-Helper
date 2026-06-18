from django.test import SimpleTestCase
from django.urls import URLPattern, URLResolver, get_resolver
from rest_framework.permissions import AllowAny


class AllowAnyAuditTests(SimpleTestCase):
    allowed_routes = {
        'api/health/',
        'api/v1/auth/register/',
        'api/v1/auth/login/',
        'api/v1/auth/send-otp/',
        'api/v1/auth/verify-otp/',
        'api/v1/auth/verify-phone/',
        'api/v1/auth/forgot-password/',
        'api/v1/auth/reset-password/',
        'api/v1/auth/google/',
        'api/v1/auth/google/config/',
        'api/v1/auth/google/start/',
        'api/v1/auth/google/callback/',
        'api/v1/auth/google/exchange/',
        'api/v1/auth/refresh/',
        'api/v1/payments/click/prepare/',
        'api/v1/payments/click/complete/',
        'api/v1/subscription/payments/click/prepare/',
        'api/v1/subscription/payments/click/complete/',
        'api/v1/subscriptions/payments/click/prepare/',
        'api/v1/subscriptions/payments/click/complete/',
        'api/v1/tenders/',
        'api/v1/tenders/<uuid:pk>/',
    }

    def _allow_any_routes(self, patterns, prefix=''):
        routes = set()
        for pattern in patterns:
            route = f'{prefix}{pattern.pattern}'
            if isinstance(pattern, URLResolver):
                routes.update(self._allow_any_routes(pattern.url_patterns, route))
                continue

            if not isinstance(pattern, URLPattern):
                continue
            view_class = getattr(pattern.callback, 'cls', None)
            permissions = getattr(view_class, 'permission_classes', ())
            if AllowAny in permissions:
                routes.add(route)
        return routes

    def test_allow_any_is_limited_to_explicit_public_endpoints(self):
        actual_routes = self._allow_any_routes(get_resolver().url_patterns)
        unexpected = actual_routes - self.allowed_routes
        self.assertEqual(unexpected, set(), f'Unexpected AllowAny routes: {sorted(unexpected)}')
