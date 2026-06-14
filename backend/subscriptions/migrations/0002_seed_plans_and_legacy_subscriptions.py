from datetime import timedelta

from django.db import migrations
from django.utils import timezone


PLAN_DATA = (
    {
        'code': 'free',
        'name': 'Free',
        'rank': 0,
        'description': 'Core tender search, calculator, and limited analysis.',
        'features': [],
        'limits': {'ai_analysis_monthly': 4},
    },
    {
        'code': 'pro',
        'name': 'Pro',
        'rank': 10,
        'description': 'Expanded analysis and notification fair-use limits.',
        'features': [],
        'limits': {'ai_analysis_monthly': 100},
    },
    {
        'code': 'business',
        'name': 'Business',
        'rank': 20,
        'description': 'Documents, competitor intelligence, and collaboration.',
        'features': [
            'document_generation',
            'document_export',
            'competitor_intelligence',
            'team_collaboration',
        ],
        'limits': {'ai_analysis_monthly': 250},
    },
    {
        'code': 'enterprise',
        'name': 'Enterprise',
        'rank': 30,
        'description': 'Business capabilities plus advanced audit controls.',
        'features': [
            'document_generation',
            'document_export',
            'competitor_intelligence',
            'team_collaboration',
            'advanced_audit',
        ],
        'limits': {'ai_analysis_monthly': 500},
    },
)


def _month_period(now):
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    return start, end


def seed_plans_and_subscriptions(apps, schema_editor):
    SubscriptionPlan = apps.get_model('subscriptions', 'SubscriptionPlan')
    CompanySubscription = apps.get_model(
        'subscriptions',
        'CompanySubscription',
    )
    CompanyProfile = apps.get_model('companies', 'CompanyProfile')

    plans = {}
    for plan_data in PLAN_DATA:
        plan, _ = SubscriptionPlan.objects.update_or_create(
            code=plan_data['code'],
            defaults={
                **plan_data,
                'price_uzs': None,
                'currency': 'UZS',
                'billing_period': 'monthly',
                'is_active': True,
                'is_public': True,
            },
        )
        plans[plan.code] = plan

    now = timezone.now()
    free_start, free_end = _month_period(now)
    for company in CompanyProfile.objects.all().iterator():
        plan = plans.get(company.current_tariff, plans['free'])
        if plan.code == 'free':
            period_start = free_start
            period_end = free_end
            status = 'active'
        elif company.tariff_expires_at and company.tariff_expires_at <= now:
            period_end = company.tariff_expires_at
            period_start = period_end - timedelta(days=30)
            status = 'expired'
        else:
            period_start = now
            period_end = company.tariff_expires_at or (now + timedelta(days=30))
            status = 'active'

        CompanySubscription.objects.create(
            company=company,
            plan=plan,
            status=status,
            source='system',
            starts_at=period_start,
            current_period_start=period_start,
            current_period_end=period_end,
            ended_at=period_end if status == 'expired' else None,
            metadata={'migrated_from': 'company_profile.current_tariff'},
        )


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            seed_plans_and_subscriptions,
            migrations.RunPython.noop,
        ),
    ]
