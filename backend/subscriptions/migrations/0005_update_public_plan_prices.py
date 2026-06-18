from django.db import migrations


def update_public_plan_prices(apps, schema_editor):
    SubscriptionPlan = apps.get_model('subscriptions', 'SubscriptionPlan')
    prices = {
        'free': 0,
        'pro': 350000,
        'business': 950000,
    }
    for code, price in prices.items():
        SubscriptionPlan.objects.filter(code=code).update(
            price_uzs=price,
            currency='UZS',
            billing_period='monthly',
        )


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0004_companysubscription_subscription_trial_period_is_valid_and_more'),
    ]

    operations = [
        migrations.RunPython(
            update_public_plan_prices,
            migrations.RunPython.noop,
        ),
    ]
