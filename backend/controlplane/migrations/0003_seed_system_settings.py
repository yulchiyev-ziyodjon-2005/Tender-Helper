from django.db import migrations


def seed_system_settings(apps, schema_editor):
    SystemSetting = apps.get_model('controlplane', 'SystemSetting')
    SystemSetting.objects.get_or_create(
        key='maintenance_banner',
        defaults={
            'value': {
                'enabled': False,
                'message': '',
                'severity': 'warning',
                'starts_at': None,
                'ends_at': None,
            },
            'version': 1,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ('controlplane', '0002_seed_feature_flags'),
    ]

    operations = [
        migrations.RunPython(
            seed_system_settings,
            migrations.RunPython.noop,
        ),
    ]
