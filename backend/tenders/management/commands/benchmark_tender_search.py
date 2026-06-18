import json
import math
import time

from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from tenders.models import TenderLot
from tenders.services.search import apply_tender_search


class Command(BaseCommand):
    help = 'Benchmark the production-equivalent tender substring search query.'

    def add_arguments(self, parser):
        parser.add_argument('--query', required=True)
        parser.add_argument('--iterations', type=int, default=20)
        parser.add_argument('--warmup', type=int, default=3)
        parser.add_argument('--limit', type=int, default=20)
        parser.add_argument('--category')
        parser.add_argument('--region')
        parser.add_argument('--platform-source')
        parser.add_argument(
            '--ordering',
            choices=(
                'posted_date',
                '-posted_date',
                'deadline',
                '-deadline',
                'start_price',
                '-start_price',
            ),
            default='-posted_date',
        )
        parser.add_argument('--explain', action='store_true')
        parser.add_argument('--allow-sqlite', action='store_true')
        parser.add_argument('--minimum-dataset-size', type=int, default=0)
        parser.add_argument('--assert-p95-ms', type=float)

    def handle(self, *args, **options):
        if connection.vendor != 'postgresql' and not options['allow_sqlite']:
            raise CommandError(
                'The production benchmark requires PostgreSQL. '
                'Use --allow-sqlite only for a local contract smoke test.'
            )
        for key in ('iterations', 'warmup', 'limit'):
            if options[key] < 1:
                raise CommandError(f'--{key.replace("_", "-")} must be positive.')

        active_lots = TenderLot.objects.filter(status=TenderLot.Status.ACTIVE)
        dataset_size = active_lots.count()
        if dataset_size < options['minimum_dataset_size']:
            raise CommandError(
                f'Active dataset has {dataset_size} rows; '
                f'{options["minimum_dataset_size"]} required.'
            )

        queryset = active_lots
        if options.get('category'):
            queryset = queryset.filter(category__iexact=options['category'])
        if options.get('region'):
            queryset = queryset.filter(region__iexact=options['region'])
        if options.get('platform_source'):
            queryset = queryset.filter(
                platform_source=options['platform_source'],
            )
        queryset = apply_tender_search(queryset, options['query']).order_by(
            options['ordering'],
            'id',
        )

        if options['explain']:
            if connection.vendor != 'postgresql':
                raise CommandError('--explain requires PostgreSQL.')
            self.stdout.write(queryset[:options['limit']].explain(
                analyze=True,
                buffers=True,
                verbose=True,
            ))

        def execute():
            return list(
                queryset.values_list('id', flat=True)[:options['limit']]
            )

        for _ in range(options['warmup']):
            execute()

        durations = []
        result_count = 0
        for _ in range(options['iterations']):
            started = time.perf_counter()
            result_count = len(execute())
            durations.append((time.perf_counter() - started) * 1000)

        ordered = sorted(durations)
        p95_index = max(math.ceil(len(ordered) * 0.95) - 1, 0)
        report = {
            'database_vendor': connection.vendor,
            'dataset_size': dataset_size,
            'query': options['query'],
            'iterations': options['iterations'],
            'limit': options['limit'],
            'result_count': result_count,
            'min_ms': round(ordered[0], 3),
            'median_ms': round(ordered[len(ordered) // 2], 3),
            'p95_ms': round(ordered[p95_index], 3),
            'max_ms': round(ordered[-1], 3),
        }
        self.stdout.write(json.dumps(report, sort_keys=True))

        threshold = options.get('assert_p95_ms')
        if threshold is not None and report['p95_ms'] > threshold:
            raise CommandError(
                f'p95 {report["p95_ms"]} ms exceeds {threshold} ms.'
            )
