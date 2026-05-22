"""
Standalone auth smoke test.

Run manually:
    python test_auth.py

Django's test discovery imports files named test_*.py, so executable smoke-test
logic must stay behind a main guard.
"""

import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    sys.path.insert(0, 'backend')

    import django
    django.setup()

    from django.core.cache import cache
    from django.test import Client
    from users.models import CustomUser

    client = Client()
    phone = '+998881234567'
    CustomUser.objects.filter(phone_number=phone).delete()
    cache.clear()

    print("=" * 55)
    print("  TenderHelper Auth API Integration Test")
    print("=" * 55)

    response = client.post(
        '/api/v1/auth/send-otp/',
        {'phone_number': phone},
        content_type='application/json',
    )
    assert response.status_code == 200, f"Send OTP failed: {response.status_code}"
    print(f"[PASS] 1. Send OTP: {response.status_code}")

    otp = cache.get('tenderhelper:otp:998881234567')
    assert otp is not None, 'OTP not found in cache'
    print(f"[PASS] 2. OTP from cache: {otp}")

    response = client.post(
        '/api/v1/auth/verify-otp/',
        {'phone_number': phone, 'otp': otp},
        content_type='application/json',
    )
    assert response.status_code == 200, f"Verify OTP failed: {response.status_code}"
    data = response.json()
    assert data['is_new_user'] is True, 'Should be new user'
    token = data['tokens']['access']
    print(f"[PASS] 3. Verify OTP: {response.status_code}")

    response = client.get('/api/v1/auth/me/', HTTP_AUTHORIZATION=f'Bearer {token}')
    assert response.status_code == 200, f"GET /me/ failed: {response.status_code}"
    assert response.json()['phone_number'] == phone
    print(f"[PASS] 4. GET /me/: {response.status_code}")

    print("=" * 55)
    print("  AUTH SMOKE TEST PASSED")
    print("=" * 55)


if __name__ == '__main__':
    main()
