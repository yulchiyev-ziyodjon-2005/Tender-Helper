from analysis.models import AITenderAnalysis

from documents.exceptions import RequiredCompanyFieldsMissing


def validate_required_company_fields(company, template):
    missing = []
    for field in template.required_company_fields:
        value = getattr(company, field, None)
        if value is None or value == '':
            missing.append(field)
    if missing:
        raise RequiredCompanyFieldsMissing(missing)


def build_context_snapshot(company, tender, analysis=None):
    snapshot = {
        'company': {
            'company_name': company.company_name,
            'stir': company.stir,
            'director_name': company.director_name,
            'legal_address': company.legal_address,
            'company_type': company.company_type,
            'has_vat': company.has_vat,
            'registration_date': (
                company.registration_date.isoformat()
                if company.registration_date
                else None
            ),
        },
        'tender': {
            'id': str(tender.id),
            'lot_number': tender.lot_number,
            'title': tender.title,
            'buyer_name': tender.buyer_name,
            'deadline': tender.deadline.isoformat(),
            'start_price': str(tender.start_price),
            'category': tender.category,
            'region': tender.region,
        },
        'analysis': None,
    }
    if analysis is not None:
        if analysis.analysis_status != AITenderAnalysis.Status.COMPLETED:
            raise ValueError('Only completed analysis can be used as context.')
        snapshot['analysis'] = {
            'id': str(analysis.id),
            'summary_text': analysis.summary_text or '',
            'requirements': analysis.requirements,
            'standards': analysis.standards,
            'red_flags': analysis.red_flags,
        }
    return snapshot
