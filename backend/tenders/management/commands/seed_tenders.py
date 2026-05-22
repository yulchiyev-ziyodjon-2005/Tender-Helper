"""
TenderHelper — seed_tenders management command
================================================
Ma'lumotlar bazasini 10 ta real ko'rinishdagi O'zbekiston tender lotlari bilan to'ldiradi.
Demo va taqdimot uchun ishlatiladi.
"""

import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from tenders.models import TenderDocumentChunk, TenderLot


TENDER_DATA = [
    {
        'lot_number': 'UZEX-2026-IT-001',
        'platform_source': 'xarid_uzex',
        'title': "Davlat soliq qo'mitasi uchun server va tarmoq jihozlarini yetkazib berish",
        'buyer_name': "O'zbekiston Respublikasi Davlat soliq qo'mitasi",
        'start_price': Decimal('2_450_000_000.00'),
        'zakalat_amount': Decimal('73_500_000.00'),
        'region': 'Toshkent shahri',
        'category': 'IT va Kompyuter jihozlari',
        'raw_portal_url': 'https://xarid.uzex.uz/lots/2026/it001',
        'chunk_text': (
            "Texnik topshiriq: Dell PowerEdge R750 server — 5 dona, "
            "HP ProLiant DL380 Gen10 — 3 dona, Cisco Catalyst 9300 switch — 10 dona. "
            "Barcha jihozlar yangi bo'lishi, ISO 9001 sertifikatiga ega bo'lishi shart. "
            "Yetkazib berish muddati — shartnoma imzolanganidan 45 kun ichida. "
            "Kafolat muddati — kamida 36 oy. O'rnatish va sozlash xizmati kiritilgan bo'lishi kerak."
        ),
    },
    {
        'lot_number': 'UZEX-2026-QUR-002',
        'platform_source': 'dxarid_uzex',
        'title': "Namangan viloyati hokimligi ma'muriy binosini kapital ta'mirlash",
        'buyer_name': 'Namangan viloyati hokimligi',
        'start_price': Decimal('4_800_000_000.00'),
        'zakalat_amount': Decimal('144_000_000.00'),
        'region': 'Namangan viloyati',
        'category': 'Qurilish va Ta\'mirlash',
        'raw_portal_url': 'https://dxarid.uzex.uz/lots/2026/qur002',
        'chunk_text': (
            "Ishlar tarkibi: asos va poydevorni mustahkamlash, tom qoplamasi almashtirish, "
            "ichki va tashqi bezak ishlari, elektr va sanitariya-texnika tarmoqlarini qayta o'rnatish. "
            "Barcha materiallar O'zDSt standartlariga mos kelishi shart. "
            "Ishlarni bajarish muddati — 180 kalendar kun. "
            "Pudratchi kamida 3 yillik qurilish tajribasiga ega bo'lishi kerak. "
            "Jarima: har bir kechiktirilgan kun uchun shartnoma summasining 0.1% miqdorida penya hisoblanadi."
        ),
    },
    {
        'lot_number': 'UZEX-2026-MEB-003',
        'platform_source': 'xarid_uzex',
        'title': "Toshkent tibbiyot akademiyasi uchun laboratoriya mebellari sotib olish",
        'buyer_name': "Toshkent tibbiyot akademiyasi",
        'start_price': Decimal('890_000_000.00'),
        'zakalat_amount': Decimal('26_700_000.00'),
        'region': 'Toshkent shahri',
        'category': 'Mebel va Jihozlar',
        'raw_portal_url': 'https://xarid.uzex.uz/lots/2026/meb003',
        'chunk_text': (
            "Laboratoriya stollari (kimyoviy chidamli qoplama bilan) — 50 dona, "
            "laboratoriya shkafi (reaktivlar uchun) — 30 dona, "
            "ergonomik laboratoriya stullari — 100 dona. "
            "Materiallar: GOST 16371-2014 standartiga mos kelishi kerak. "
            "Rang va o'lchamlar buyurtmachining texnik topshirig'iga muvofiq. "
            "Yetkazib berish va o'rnatish bir narxga kiritilgan bo'lishi lozim."
        ),
    },
    {
        'lot_number': 'UZEX-2026-TIB-004',
        'platform_source': 'dxarid_uzex',
        'title': "Buxoro viloyat ko'p tarmoqli tibbiyot markazi uchun tibbiy uskunalar",
        'buyer_name': "Buxoro viloyat ko'p tarmoqli tibbiyot markazi",
        'start_price': Decimal('3_200_000_000.00'),
        'zakalat_amount': Decimal('96_000_000.00'),
        'region': 'Buxoro viloyati',
        'category': 'Tibbiyot jihozlari',
        'raw_portal_url': 'https://dxarid.uzex.uz/lots/2026/tib004',
        'chunk_text': (
            "Sotib olinadigan uskunalar: ultratovush diagnostika apparati (Mindray DC-70) — 2 dona, "
            "raqamli rentgen apparati — 1 dona, laboratoriya analizatori (gematologik) — 3 dona. "
            "Barcha uskunalar faqat yangi bo'lishi, ishlab chiqaruvchining rasmiy kafolati bilan kelishi shart. "
            "ISO 13485 tibbiy uskunalar sifat menejment sertifikati talab qilinadi. "
            "O'rnatish, ta'lim va texnik xizmat ko'rsatish shartnomaga kiritilishi kerak."
        ),
    },
    {
        'lot_number': 'UZEX-2026-TR-005',
        'platform_source': 'xarid_uzex',
        'title': "Samarqand viloyati yo'l-transport boshqarmasi uchun maxsus texnika sotib olish",
        'buyer_name': "Samarqand viloyati yo'l-transport boshqarmasi",
        'start_price': Decimal('1_750_000_000.00'),
        'zakalat_amount': Decimal('52_500_000.00'),
        'region': 'Samarqand viloyati',
        'category': 'Transport va Maxsus texnika',
        'raw_portal_url': 'https://xarid.uzex.uz/lots/2026/tr005',
        'chunk_text': (
            "Sotib olinadigan texnika: avtograyder — 2 dona, asfalt yotqizgich (5 tonna) — 1 dona, "
            "vibratsion katok (10 tonna) — 2 dona. "
            "Ishlab chiqarish yili — 2025 yoki undan keyin. "
            "Ehtiyot qismlar va texnik xizmat kamida 2 yil kafolatlanishi kerak. "
            "Yetkazib berish punkti: Samarqand shahri, viloyat yo'l fondi bazasi."
        ),
    },
    {
        'lot_number': 'UZEX-2026-IT-006',
        'platform_source': 'dxarid_uzex',
        'title': "Raqamli texnologiyalar vazirligi uchun korporativ dasturiy ta'minot litsenziyalari",
        'buyer_name': "O'zbekiston Respublikasi Raqamli texnologiyalar vazirligi",
        'start_price': Decimal('680_000_000.00'),
        'zakalat_amount': Decimal('20_400_000.00'),
        'region': 'Toshkent shahri',
        'category': "IT va Dasturiy ta'minot",
        'raw_portal_url': 'https://dxarid.uzex.uz/lots/2026/it006',
        'chunk_text': (
            "Microsoft 365 E3 litsenziya — 200 dona (1 yillik obuna), "
            "Windows Server 2022 Datacenter — 5 litsenziya, "
            "Microsoft SQL Server Enterprise — 3 litsenziya. "
            "Barcha litsenziyalar rasmiy Microsoft partnyor orqali sotib olinishi shart. "
            "Litsenziya hujjatlari va aktivatsiya kodlari shartnomada ko'rsatilishi kerak. "
            "Faqat rasmiy kanal orqali sotib olingan litsenziyalar qabul qilinadi."
        ),
    },
    {
        'lot_number': 'UZEX-2026-OZ-007',
        'platform_source': 'xarid_uzex',
        'title': "Farg'ona viloyati ta'lim boshqarmasi uchun ovqatlanish mahsulotlari yetkazib berish",
        'buyer_name': "Farg'ona viloyati xalq ta'limi boshqarmasi",
        'start_price': Decimal('1_200_000_000.00'),
        'zakalat_amount': Decimal('36_000_000.00'),
        'region': "Farg'ona viloyati",
        'category': 'Oziq-ovqat mahsulotlari',
        'raw_portal_url': 'https://xarid.uzex.uz/lots/2026/oz007',
        'chunk_text': (
            "Maktab ovqatlanish tizimi uchun 6 oylik yetkazib berish: "
            "go'sht mahsulotlari (mol go'shti, tovuq go'shti), sut mahsulotlari, "
            "don mahsulotlari (un, guruch, makaron), sabzavot va mevalar. "
            "Barcha mahsulotlar O'zDSt sanitariya normalariga mos kelishi shart. "
            "Yetkazib berish haftalik asosda, 45 ta maktabga. "
            "Harorat rejimiga rioya qilinishi va sovutish transport vositasi mavjudligi tekshiriladi."
        ),
    },
    {
        'lot_number': 'UZEX-2026-XAV-008',
        'platform_source': 'dxarid_uzex',
        'title': "Xorazm viloyati FHDYoI uchun xavfsizlik kameralari tizimini o'rnatish",
        'buyer_name': "Xorazm viloyati Favqulodda holatlarda davlat yordami inspeksiyasi",
        'start_price': Decimal('520_000_000.00'),
        'zakalat_amount': Decimal('15_600_000.00'),
        'region': 'Xorazm viloyati',
        'category': 'Xavfsizlik tizimlari',
        'raw_portal_url': 'https://dxarid.uzex.uz/lots/2026/xav008',
        'chunk_text': (
            "O'rnatish ishlari: IP kameralar (Hikvision DS-2CD2T46G2-4I) — 50 dona, "
            "NVR video yozish qurilmasi (32 kanalli) — 2 dona, "
            "monitor (43 dyuym) — 4 dona, kabel va aksessuarlar to'plami. "
            "Tizim 24/7 rejimida ishlashi va kamida 30 kunlik yozuvni saqlashi kerak. "
            "O'rnatish, sozlash va 12 oylik texnik qo'llab-quvvatlash narxga kiritilsin."
        ),
    },
    {
        'lot_number': 'UZEX-2026-ENR-009',
        'platform_source': 'xarid_uzex',
        'title': "Qashqadaryo viloyat kasalxonasi uchun quyosh panellari o'rnatish",
        'buyer_name': "Qashqadaryo viloyat ko'p tarmoqli kasalxonasi",
        'start_price': Decimal('950_000_000.00'),
        'zakalat_amount': Decimal('28_500_000.00'),
        'region': 'Qashqadaryo viloyati',
        'category': 'Energetika va Muqobil energiya',
        'raw_portal_url': 'https://xarid.uzex.uz/lots/2026/enr009',
        'chunk_text': (
            "Loyiha: 100 kVt quvvatga ega quyosh elektr stansiyasi o'rnatish. "
            "Quyosh panellari (monokristall, samaradorligi kamida 21%) — 200 dona, "
            "invertor (50 kVt) — 2 dona, montaj konstruksiyalari va kabellar. "
            "Loyiha hujjatlari, o'rnatish va ulanish ishlari narxga kiritilsin. "
            "Kafolat muddati — kamida 10 yil (panellar uchun 25 yil). "
            "ISO 14001 ekologik menejment sertifikati talab qilinadi."
        ),
    },
    {
        'lot_number': 'UZEX-2026-TAL-010',
        'platform_source': 'dxarid_uzex',
        'title': "Andijon viloyati maktablari uchun zamonaviy o'quv jihozlari sotib olish",
        'buyer_name': "Andijon viloyati xalq ta'limi boshqarmasi",
        'start_price': Decimal('430_000_000.00'),
        'zakalat_amount': Decimal('12_900_000.00'),
        'region': 'Andijon viloyati',
        'category': "Ta'lim jihozlari",
        'raw_portal_url': 'https://dxarid.uzex.uz/lots/2026/tal010',
        'chunk_text': (
            "Interaktiv doska (86 dyuym, sensorli) — 30 dona, "
            "multimedia proyektor (4000 lumen) — 30 dona, "
            "noutbuk (Intel i5, 8GB RAM, 256GB SSD) — 30 dona. "
            "Barcha jihozlar brend mahsulot bo'lishi shart (Samsung, Epson, Lenovo ekvivalenti). "
            "Yetkazib berish va o'rnatish 30 ta maktabga amalga oshiriladi. "
            "O'qituvchilar uchun 1 kunlik ta'lim trenining o'tkazilishi kerak."
        ),
    },
]


class Command(BaseCommand):
    help = "Ma'lumotlar bazasini 10 ta real ko'rinishdagi O'zbekiston tender lotlari bilan to'ldiradi"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help="Avval mavjud barcha tender lotlarini o'chiradi",
        )

    def handle(self, *args, **options):
        if options['clear']:
            count, _ = TenderLot.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"  {count} ta mavjud yozuv o'chirildi"))

        now = timezone.now()
        created_count = 0

        for data in TENDER_DATA:
            lot_number = data['lot_number']

            # Skip if already exists
            if TenderLot.objects.filter(lot_number=lot_number).exists():
                self.stdout.write(self.style.NOTICE(f"  [INFO]  {lot_number} - allaqachon mavjud, o'tkazildi"))
                continue

            # Random deadline 5-30 days from now
            deadline_days = random.randint(5, 30)
            posted_days_ago = random.randint(1, 5)

            tender = TenderLot.objects.create(
                lot_number=lot_number,
                platform_source=data['platform_source'],
                title=data['title'],
                buyer_name=data['buyer_name'],
                start_price=data['start_price'],
                zakalat_amount=data['zakalat_amount'],
                region=data['region'],
                category=data['category'],
                posted_date=now - timedelta(days=posted_days_ago),
                deadline=now + timedelta(days=deadline_days),
                status=TenderLot.Status.ACTIVE,
                raw_portal_url=data.get('raw_portal_url', ''),
            )

            TenderDocumentChunk.objects.create(
                tender_lot=tender,
                file_name='texnik-topshiriq.pdf',
                chunk_index=0,
                raw_text=data['chunk_text'],
            )

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"  [OK]: {lot_number} - {data['title'][:60]}..."
                )
            )

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f"Jami {created_count} ta yangi tender lot yaratildi! [OK]"
            )
        )
