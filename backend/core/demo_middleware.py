"""
TenderHelper — Demo Mode Middleware
====================================
Har bir so'rovda avtomatik ravishda demo foydalanuvchini request.user ga biriktiradi.
Bu autentifikatsiya talab qilmasdan demo rejimda ishlash imkonini beradi.
"""

from django.contrib.auth import get_user_model

User = get_user_model()


class DemoUserMiddleware:
    """
    Middleware that automatically assigns a demo user to every request.
    This ensures all request.user references work without authentication.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get or create demo user
        demo_user, created = User.objects.get_or_create(
            email='demo@tenderhelper.uz',
            defaults={
                'phone_number': '+998901234567',
                'full_name': 'Demo Foydalanuvchi',
                'role': 'user',
                'auth_provider': 'phone',
                'is_active': True,
            },
        )

        if created:
            demo_user.set_unusable_password()
            demo_user.save()

        # Always assign demo user to request
        request.user = demo_user

        # Get or create CompanyProfile for demo user
        from companies.models import CompanyProfile

        CompanyProfile.objects.get_or_create(
            user=demo_user,
            defaults={
                'company_name': 'Demo Kompaniya MChJ',
                'stir': '123456789',
                'industry': 'IT va Dasturlash',
                'has_vat': True,
                'company_type': 'mchj',
                'experience_level': 'intermediate',
            },
        )

        response = self.get_response(request)
        return response
