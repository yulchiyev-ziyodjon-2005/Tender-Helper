import re
import unicodedata


def _normalize_text(value):
    normalized = unicodedata.normalize('NFKC', str(value or '')).strip()
    return re.sub(r'\s+', ' ', normalized)


def normalize_competitor_name(value):
    normalized = _normalize_text(value)
    if not normalized:
        raise ValueError('Competitor name cannot be empty.')
    return normalized


def normalize_category(value):
    normalized = _normalize_text(value)
    if not normalized:
        raise ValueError('Category cannot be empty.')
    return normalized.casefold()


def build_identity_key(normalized_name, stir=''):
    stir = str(stir or '').strip()
    if stir:
        if len(stir) != 9 or not stir.isdigit():
            raise ValueError('STIR must contain exactly 9 digits.')
        return f'stir:{stir}'
    comparable_name = re.sub(
        r'[^\w]+',
        ' ',
        normalized_name.casefold(),
        flags=re.UNICODE,
    )
    comparable_name = re.sub(r'\s+', ' ', comparable_name).strip()
    return f'name:{comparable_name}'
