from django.db import migrations


FEATURES = (
    'document_generation',
    'document_export',
    'competitor_intelligence',
    'team_collaboration',
    'advanced_audit',
)


def seed_feature_flags(apps, schema_editor):
    FeatureFlag = apps.get_model('controlplane', 'FeatureFlag')
    for feature in FEATURES:
        FeatureFlag.objects.get_or_create(
            feature=feature,
            defaults={
                'is_enabled': True,
                'reason': '',
                'version': 1,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ('controlplane', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            seed_feature_flags,
            migrations.RunPython.noop,
        ),
    ]
