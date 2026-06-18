from urllib.parse import urlparse

from analysis.models import LegalKnowledgeSource


OFFICIAL_LEGAL_SOURCE_POLICIES = (
    {
        'code': 'lex_uz',
        'name': "O'zbekiston Respublikasi Qonunchilik ma'lumotlari milliy bazasi",
        'authority_level': LegalKnowledgeSource.AuthorityLevel.PRIMARY_NORMATIVE,
        'base_url': 'https://lex.uz/',
        'allowed_domains': ['lex.uz'],
        'source_rank': 10,
        'requires_effective_date_check': True,
        'requires_manual_review': False,
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
        'authority_level': LegalKnowledgeSource.AuthorityLevel.OFFICIAL_CONTEXT,
        'base_url': 'https://gov.uz/oz/pages/davlat_xaridlari',
        'allowed_domains': ['gov.uz'],
        'source_rank': 20,
        'requires_effective_date_check': True,
        'requires_manual_review': False,
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
        'name': "Davlat xaridlarining maxsus axborot portali",
        'authority_level': LegalKnowledgeSource.AuthorityLevel.OFFICIAL_CONTEXT,
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
        'name': "Verified Uzbekistan technical standards source",
        'authority_level': LegalKnowledgeSource.AuthorityLevel.TECHNICAL_STANDARD,
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


def sync_official_legal_sources():
    sources = []
    for policy in OFFICIAL_LEGAL_SOURCE_POLICIES:
        data = {
            'name': policy['name'],
            'authority_level': policy['authority_level'],
            'base_url': policy['base_url'],
            'allowed_domains': policy['allowed_domains'],
            'source_rank': policy['source_rank'],
            'requires_effective_date_check': policy['requires_effective_date_check'],
            'requires_manual_review': policy['requires_manual_review'],
            'is_active': policy.get('is_active', True),
            'metadata': policy['metadata'],
        }
        source, _ = LegalKnowledgeSource.objects.update_or_create(
            code=policy['code'],
            defaults=data,
        )
        sources.append(source)
    return sources


def is_allowed_legal_source_url(url, *, active_only=True):
    parsed = urlparse(url)
    host = parsed.hostname or ''
    if parsed.scheme != 'https':
        return False
    sources = LegalKnowledgeSource.objects.all()
    if active_only:
        sources = sources.filter(is_active=True)
    for source in sources:
        if host in set(source.allowed_domains):
            return True
    return False
