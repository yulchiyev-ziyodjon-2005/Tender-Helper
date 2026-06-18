from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.utils import timezone

from tenders.models import TenderLot, TenderSource

BENCHMARK_PREFIX = 'BENCH-SEARCH-'


class Command(BaseCommand):
    help = 'Create deterministic synthetic tender rows for search benchmarks.'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100000)
        parser.add_argument('--batch-size', type=int, default=5000)
        parser.add_argument('--reset', action='store_true')
        parser.add_argument('--allow-non-test', action='store_true')

    def handle(self, *args, **options):
        if (
            settings.APP_ENV != 'test'
            and not options['allow_non_test']
        ):
            raise CommandError(
                'Synthetic benchmark data is restricted to APP_ENV=test. '
                'Use --allow-non-test explicitly for an isolated local DB.'
            )
        count = options['count']
        batch_size = options['batch_size']
        if count < 1 or count > 1_000_000:
            raise CommandError('--count must be between 1 and 1000000.')
        if batch_size < 1 or batch_size > 20000:
            raise CommandError('--batch-size must be between 1 and 20000.')

        benchmark_rows = TenderLot.objects.filter(
            lot_number__startswith=BENCHMARK_PREFIX,
        )
        existing = benchmark_rows.count()
        if options['reset']:
            benchmark_rows.delete()
            existing = 0
        elif existing:
            raise CommandError(
                f'{existing} benchmark rows already exist. Use --reset.'
            )

        now = timezone.now()
        sources = {
            source.code: source
            for source in TenderSource.objects.filter(
                code__in=[
                    TenderLot.PlatformSource.XARID_UZEX,
                    TenderLot.PlatformSource.DXARID_UZEX,
                ],
            )
        }
        created = 0
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            rows = []
            for index in range(batch_start, batch_end):
                is_match = index % 100 == 0
                platform_source = (
                    TenderLot.PlatformSource.XARID_UZEX
                    if index % 2 == 0
                    else TenderLot.PlatformSource.DXARID_UZEX
                )
                lot_number = f'{BENCHMARK_PREFIX}{index:07d}'
                rows.append(TenderLot(
                    source=sources[platform_source],
                    external_id=lot_number,
                    lot_number=lot_number,
                    platform_source=platform_source,
                    title=(
                        f'Specialized server procurement package {index}'
                        if is_match
                        else f'Routine public procurement package {index}'
                    ),
                    buyer_name=(
                        'Digital Infrastructure Ministry'
                        if is_match
                        else f'Regional Public Buyer {index % 500}'
                    ),
                    start_price=1_000_000 + index,
                    region='Toshkent' if index % 4 == 0 else 'Samarqand',
                    category=(
                        'IT Infrastructure'
                        if is_match
                        else f'General Category {index % 50}'
                    ),
                    posted_date=now - timedelta(minutes=index % 10000),
                    deadline=now + timedelta(days=(index % 30) + 1),
                    status=TenderLot.Status.ACTIVE,
                ))
            TenderLot.objects.bulk_create(rows, batch_size=batch_size)
            created += len(rows)
            self.stdout.write(f'Created {created}/{count} benchmark rows.')

        if connection.vendor == 'postgresql':
            with connection.cursor() as cursor:
                cursor.execute('ANALYZE tender_lots')
        self.stdout.write(self.style.SUCCESS(
            f'Created {created} deterministic benchmark rows.'
        ))
