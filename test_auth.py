"""
TenderHelper — Auth API Integration Test
==========================================
To'liq auth flow: OTP send → verify → JWT → /me/
"""
import os, sys, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
sys.path.insert(0, 'backend')
django.setup()

from django.test import Client
from django.core.cache import cache

c = Client()

print("=" * 55)
print("  TenderHelper Auth API Integration Test")
print("=" * 55)

# ──── 1. Send OTP ────
phone = '+998881234567'
r1 = c.post('/api/v1/auth/send-otp/',
    {'phone_number': phone},
    content_type='application/json')
assert r1.status_code == 200, f"Send OTP failed: {r1.status_code}"
print(f"[PASS] 1. Send OTP: {r1.status_code} - {r1.json()['message']}")

# ──── 2. Get OTP from cache ────
otp_key = 'tenderhelper:otp:998881234567'
otp = cache.get(otp_key)
assert otp is not None, "OTP not found in cache"
print(f"[PASS] 2. OTP from cache: {otp}")

# ──── 3. Verify OTP → JWT ────
r2 = c.post('/api/v1/auth/verify-otp/',
    {'phone_number': phone, 'otp': otp},
    content_type='application/json')
assert r2.status_code == 200, f"Verify OTP failed: {r2.status_code} - {r2.content}"
data = r2.json()
assert 'tokens' in data, "No tokens in response"
assert data['is_new_user'] == True, "Should be new user"
token = data['tokens']['access']
print(f"[PASS] 3. Verify OTP: {r2.status_code} - is_new_user={data['is_new_user']}")
print(f"       User ID: {data['user']['id']}")
print(f"       Token: {token[:50]}...")

# ──── 4. GET /me/ with JWT ────
r3 = c.get('/api/v1/auth/me/',
    HTTP_AUTHORIZATION=f'Bearer {token}')
assert r3.status_code == 200, f"GET /me/ failed: {r3.status_code}"
me = r3.json()
assert me['phone_number'] == phone, "Phone mismatch"
print(f"[PASS] 4. GET /me/: {r3.status_code} - phone={me['phone_number']}")

# ──── 5. PATCH /me/ ────
r4 = c.patch('/api/v1/auth/me/',
    {'full_name': 'Test User', 'email': 'test@example.com'},
    content_type='application/json',
    HTTP_AUTHORIZATION=f'Bearer {token}')
assert r4.status_code == 200, f"PATCH /me/ failed: {r4.status_code}"
updated = r4.json()
assert updated['full_name'] == 'Test User'
print(f"[PASS] 5. PATCH /me/: {r4.status_code} - full_name={updated['full_name']}")

# ──── 6. Token Refresh ────
refresh_token = data['tokens']['refresh']
r5 = c.post('/api/v1/auth/refresh/',
    {'refresh': refresh_token},
    content_type='application/json')
assert r5.status_code == 200, f"Token refresh failed: {r5.status_code}"
print(f"[PASS] 6. Token Refresh: {r5.status_code} - new access token received")

# ──── 7. Invalid OTP test ────
cache.clear()
r6 = c.post('/api/v1/auth/verify-otp/',
    {'phone_number': phone, 'otp': '000000'},
    content_type='application/json')
assert r6.status_code == 400, f"Invalid OTP should return 400: {r6.status_code}"
print(f"[PASS] 7. Invalid OTP: {r6.status_code} - {r6.json()['error']}")

# ──── 8. Rate limit test ────
c.post('/api/v1/auth/send-otp/',
    {'phone_number': '+998990001122'},
    content_type='application/json')
r7 = c.post('/api/v1/auth/send-otp/',
    {'phone_number': '+998990001122'},
    content_type='application/json')
assert r7.status_code == 429, f"Rate limit should return 429: {r7.status_code}"
print(f"[PASS] 8. Rate Limit: {r7.status_code} - Correctly blocked")

print("\n" + "=" * 55)
print("  ALL 8 TESTS PASSED!")
print("=" * 55)
