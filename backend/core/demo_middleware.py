import logging
from django.contrib.auth import get_user_model
from companies.models import CompanyProfile

logger = logging.getLogger(__name__)
User = get_user_model()

class DemoUserMiddleware:
    """
    Vaqtinchalik middleware: barcha so'rovlarni avtomatik ravishda
    'demo_user' foydalanuvchisi sifatida qabul qiladi va u uchun
    zarur bo'lgan kompaniya profilini yaratadi.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Faqat /api/ URL'lari uchun ishlaydi
        if request.path.startswith('/api/'):
            user, created = User.objects.get_or_create(
                email='demo@tenderhelper.uz',
                defaults={
                    'phone_number': '+998901234567',
                    'full_name': 'Demo Foydalanuvchi'
                }
            )
            
            # Agar yangi yaratilgan bo'lsa parolni ham o'rnatib qo'yamiz (har ehtimolga qarshi)
            if created:
                user.set_password('demo1234')
                user.save()

            # Kompaniya profilini ta'minlash
            profile, profile_created = CompanyProfile.objects.get_or_create(
                user=user,
                defaults={
                    'company_name': 'Demo Kompaniya MChJ',
                    'stir': '123456789',
                    'company_type': 'mchj',
                    'industry': 'IT va Dasturlash',
                    'has_vat': True
                }
            )

            # Requestga ushbu user'ni biriktirish
            request.user = user

        response = self.get_response(request)
        return response
