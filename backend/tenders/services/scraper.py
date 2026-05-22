import logging
from datetime import timedelta
from django.utils import timezone
from tenders.models import TenderLot

logger = logging.getLogger(__name__)

class UzExScraper:
    """
    Davlat xaridlari (xarid.uzex.uz) saytidan tenderlarni yuklab olish xizmati.
    Hozirgi bosqichda Mock ma'lumotlar orqali ishlaydi (Real API ulanmaguncha).
    """

    def __init__(self):
        self.base_url = "https://xarid.uzex.uz/api/v1/tenders" # Placeholder

    def fetch_latest_tenders(self, limit=10):
        """
        Eng so'nggi tenderlarni tortib olish va bazaga saqlash.
        """
        logger.info(f"xarid.uzex.uz saytidan eng so'nggi {limit} ta tender olinmoqda...")
        
        # TODO: Requests yoki httpx orqali real ulanish qilinadi.
        # Hozircha mock data:
        mock_data = [
            {
                "lot_number": "24110012",
                "title": "Kompyuter texnikalari va server uskunalarini xarid qilish",
                "buyer_name": "Raqamli Texnologiyalar Vazirligi",
                "start_price": 1250000000.00,
                "category": "IT uskunalar",
                "deadline_days": 10
            },
            {
                "lot_number": "24110085",
                "title": "Yangi ofis binosi uchun zamonaviy mebel jihozlari",
                "buyer_name": "O'zsanoatqurilishbank ATB",
                "start_price": 450000000.00,
                "category": "Mebel",
                "deadline_days": 5
            }
        ]

        saved_count = 0
        for item in mock_data:
            obj, created = TenderLot.objects.get_or_create(
                lot_number=item['lot_number'],
                defaults={
                    'platform_source': TenderLot.PlatformSource.XARID_UZEX,
                    'title': item['title'],
                    'buyer_name': item['buyer_name'],
                    'start_price': item['start_price'],
                    'zakalat_amount': item['start_price'] * 0.03, # 3% zakalat
                    'category': item['category'],
                    'posted_date': timezone.now(),
                    'deadline': timezone.now() + timedelta(days=item['deadline_days']),
                    'status': TenderLot.Status.ACTIVE,
                    'raw_portal_url': f"https://xarid.uzex.uz/purchase/competition/detail/{item['lot_number']}"
                }
            )
            if created:
                saved_count += 1
                logger.info(f"Yangi lot saqlandi: {obj.lot_number}")
        
        return saved_count

def run_scraper_task():
    """Celery kabi background task runnerlar uchun asosiy funksiya"""
    scraper = UzExScraper()
    return scraper.fetch_latest_tenders()
