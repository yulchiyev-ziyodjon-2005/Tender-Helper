from django.db import migrations


INDEX_SQL = (
    (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'tender_title_upper_trgm_gin ON tender_lots '
        'USING gin (UPPER(title) gin_trgm_ops)',
        'DROP INDEX CONCURRENTLY IF EXISTS tender_title_upper_trgm_gin',
    ),
    (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'tender_buyer_upper_trgm_gin ON tender_lots '
        'USING gin (UPPER(buyer_name) gin_trgm_ops)',
        'DROP INDEX CONCURRENTLY IF EXISTS tender_buyer_upper_trgm_gin',
    ),
    (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'tender_lot_no_upper_trgm_gin ON tender_lots '
        'USING gin (UPPER(lot_number) gin_trgm_ops)',
        'DROP INDEX CONCURRENTLY IF EXISTS tender_lot_no_upper_trgm_gin',
    ),
    (
        'CREATE INDEX CONCURRENTLY IF NOT EXISTS '
        'tender_category_upper_trgm_gin ON tender_lots '
        'USING gin (UPPER(category) gin_trgm_ops)',
        'DROP INDEX CONCURRENTLY IF EXISTS tender_category_upper_trgm_gin',
    ),
)


def create_postgresql_search_indexes(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')
    for create_sql, _ in INDEX_SQL:
        schema_editor.execute(create_sql)


def drop_postgresql_search_indexes(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    for _, drop_sql in reversed(INDEX_SQL):
        schema_editor.execute(drop_sql)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('tenders', '0002_tenderlot_created_by'),
    ]

    operations = [
        migrations.RunPython(
            create_postgresql_search_indexes,
            drop_postgresql_search_indexes,
        ),
    ]
