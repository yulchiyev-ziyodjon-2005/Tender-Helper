import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenders', '0004_tendersource_tenderlot_external_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tenderlot',
            name='source',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='lots',
                to='tenders.tendersource',
            ),
        ),
        migrations.RemoveConstraint(
            model_name='tenderlot',
            name='tender_external_id_requires_source',
        ),
        migrations.AddConstraint(
            model_name='tenderlot',
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(
                        ('external_id', ''),
                        ('platform_source', 'manual'),
                    ),
                    models.Q(
                        models.Q(('platform_source', 'manual'), _negated=True),
                        models.Q(('external_id', ''), _negated=True),
                    ),
                    _connector='OR',
                ),
                name='tender_external_identity_matches_source_type',
            ),
        ),
    ]
