from django.db import migrations


SOURCE_POLICIES = (
    {
        'code': 'lex_uz',
        'name': "O'zbekiston Respublikasi Qonunchilik ma'lumotlari milliy bazasi",
        'authority_level': 'primary_normative',
        'base_url': 'https://lex.uz/',
        'allowed_domains': ['lex.uz'],
        'source_rank': 10,
        'requires_effective_date_check': True,
        'requires_manual_review': False,
        'is_active': True,
        'metadata': {
            'scope': [
                'laws',
                'presidential_acts',
                'cabinet_resolutions',
                'registered_normative_acts',
            ],
            'rag_rule': (
                'Use as the primary source for binding normative text. '
                'Always store document version and effective dates.'
            ),
        },
    },
    {
        'code': 'gov_uz_procurement',
        'name': "O'zbekiston Respublikasi Hukumat portali - davlat xaridlari",
        'authority_level': 'official_context',
        'base_url': 'https://gov.uz/oz/pages/davlat_xaridlari',
        'allowed_domains': ['gov.uz'],
        'source_rank': 20,
        'requires_effective_date_check': True,
        'requires_manual_review': False,
        'is_active': True,
        'metadata': {
            'scope': ['official_procurement_context', 'official_links'],
            'rag_rule': (
                'Use for official procurement context and links to authoritative '
                'procurement resources. Do not override Lex.uz normative text.'
            ),
        },
    },
    {
        'code': 'public_procurement_portal',
        'name': 'Davlat xaridlarining maxsus axborot portali',
        'authority_level': 'official_context',
        'base_url': 'https://xarid.mf.uz/',
        'allowed_domains': [
            'xarid.mf.uz',
            'xarid-mf.imv.uz',
            'xarid.uzex.uz',
            'etender.uzex.uz',
        ],
        'source_rank': 30,
        'requires_effective_date_check': True,
        'requires_manual_review': False,
        'is_active': True,
        'metadata': {
            'scope': [
                'procurement_announcements',
                'procurement_results',
                'operator_portal_data',
            ],
            'rag_rule': (
                'Use for procurement facts, notices and results. Legal reasoning '
                'must cite Lex.uz when a binding rule is needed.'
            ),
        },
    },
    {
        'code': 'technical_standards_verified',
        'name': 'Verified Uzbekistan technical standards source',
        'authority_level': 'technical_standard',
        'base_url': 'https://lex.uz/',
        'allowed_domains': ['lex.uz'],
        'source_rank': 60,
        'requires_effective_date_check': True,
        'requires_manual_review': True,
        'is_active': False,
        'metadata': {
            'scope': ['technical_standards', 'mandatory_certification_rules'],
            'rag_rule': (
                'Technical standards become authoritative only after their '
                'official catalog/source is verified and manually approved.'
            ),
        },
    },
)


def seed_sources(apps, schema_editor):
    LegalKnowledgeSource = apps.get_model('analysis', 'LegalKnowledgeSource')
    for policy in SOURCE_POLICIES:
        code = policy['code']
        defaults = {key: value for key, value in policy.items() if key != 'code'}
        LegalKnowledgeSource.objects.update_or_create(
            code=code,
            defaults=defaults,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0004_legalknowledgesource_legalknowledgedocument_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_sources, migrations.RunPython.noop),
    ]
