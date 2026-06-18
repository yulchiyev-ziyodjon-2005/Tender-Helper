COMPANY_CONTEXT_FIELDS = {
    'stir',
    'company_name',
    'director_name',
    'legal_address',
    'company_type',
    'has_vat',
    'registration_date',
}

CANONICAL_DOCUMENT_VERSION = 1
MAX_DOCUMENT_NODES = 2000
MAX_DOCUMENT_TEXT_CHARS = 200000

BLOCK_NODE_TYPES = {
    'paragraph',
    'heading',
    'bullet_list',
    'ordered_list',
    'list_item',
    'table',
    'table_row',
    'table_cell',
}

INLINE_NODE_TYPES = {'text'}
ALLOWED_MARKS = {'bold', 'italic', 'underline'}

ALLOWED_HTML_TAGS = {
    'p',
    'h1',
    'h2',
    'h3',
    'h4',
    'ul',
    'ol',
    'li',
    'strong',
    'em',
    'u',
    'table',
    'thead',
    'tbody',
    'tr',
    'th',
    'td',
    'br',
}

ALLOWED_HTML_ATTRIBUTES = {
    'th': ['colspan', 'rowspan'],
    'td': ['colspan', 'rowspan'],
}
