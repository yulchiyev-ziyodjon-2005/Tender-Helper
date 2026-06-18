from django.db import migrations


CONTENT_SCHEMA = {
    'type': 'document',
    'version': 1,
    'allowed_nodes': [
        'paragraph',
        'heading',
        'bullet_list',
        'ordered_list',
        'list_item',
        'table',
        'table_row',
        'table_cell',
        'text',
    ],
    'allowed_marks': ['bold', 'italic', 'underline'],
}

TEMPLATE_TYPES = (
    (
        'tender-application',
        'application',
        'Tenderda qatnashish arizasi',
        'Заявка на участие в тендере',
        (
            'Prepare a formal tender participation application using only '
            'the supplied company and tender facts. Include addressee, '
            'subject, participation intent, factual commitments, and '
            'signature block. Do not claim unavailable certificates.'
        ),
    ),
    (
        'guarantee-letter',
        'guarantee',
        'Kafolat xati',
        'Гарантийное письмо',
        (
            'Prepare a formal guarantee letter limited to commitments that '
            'are explicitly supported by the supplied context. Do not invent '
            'delivery dates, amounts, licenses, or legal guarantees.'
        ),
    ),
    (
        'commercial-proposal',
        'commercial',
        'Tijorat taklifi',
        'Коммерческое предложение',
        (
            'Prepare a structured commercial proposal. Use supplied prices '
            'only; when no price is supplied, leave an explicit editable '
            'placeholder instead of calculating or inventing a value.'
        ),
    ),
    (
        'technical-compliance',
        'compliance',
        'Texnik muvofiqlik xati',
        'Письмо о техническом соответствии',
        (
            'Prepare a technical compliance letter mapping only supplied '
            'verified requirements to company commitments. Mark unsupported '
            'or unverified requirements as requiring user review.'
        ),
    ),
    (
        'official-letter',
        'other',
        'Rasmiy tender xati',
        'Официальное тендерное письмо',
        (
            'Prepare a neutral formal letter related to the tender and the '
            'user instructions. Use only supplied facts and include an '
            'editable subject and signature block.'
        ),
    ),
)

REQUIRED_FIELDS = [
    'stir',
    'company_name',
    'director_name',
    'legal_address',
    'company_type',
]


def seed_templates(apps, schema_editor):
    Template = apps.get_model('documents', 'TenderDocumentTemplate')
    SubscriptionPlan = apps.get_model('subscriptions', 'SubscriptionPlan')

    for code, document_type, uz_name, ru_name, prompt in TEMPLATE_TYPES:
        for language, name in (('uz', uz_name), ('ru', ru_name)):
            Template.objects.update_or_create(
                code=code,
                language=language,
                version=1,
                defaults={
                    'name': name,
                    'document_type': document_type,
                    'prompt_template': (
                        f'{prompt} Output language: {language}.'
                    ),
                    'content_schema': CONTENT_SCHEMA,
                    'required_company_fields': REQUIRED_FIELDS,
                    'is_active': True,
                    'is_published': True,
                },
            )

    for code in ('business', 'enterprise'):
        plan = SubscriptionPlan.objects.filter(code=code).first()
        if plan is None:
            continue
        limits = dict(plan.limits or {})
        limits.setdefault('document_generation_monthly', None)
        limits.setdefault('document_export_monthly', None)
        plan.limits = limits
        plan.save(update_fields=['limits', 'updated_at'])


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
        ('subscriptions', '0002_seed_plans_and_legacy_subscriptions'),
    ]

    operations = [
        migrations.RunPython(seed_templates, migrations.RunPython.noop),
    ]
