from html import escape

import bleach

from documents.constants import (
    ALLOWED_HTML_ATTRIBUTES,
    ALLOWED_HTML_TAGS,
    ALLOWED_MARKS,
    CANONICAL_DOCUMENT_VERSION,
    INLINE_NODE_TYPES,
    MAX_DOCUMENT_NODES,
    MAX_DOCUMENT_TEXT_CHARS,
)
from documents.exceptions import InvalidDocumentContent


def validate_content(content):
    errors = []
    if not isinstance(content, dict):
        raise InvalidDocumentContent(['Root must be an object.'])
    if content.get('type') != 'document':
        errors.append('Root type must be document.')
    if content.get('version') != CANONICAL_DOCUMENT_VERSION:
        errors.append(
            f'Root version must be {CANONICAL_DOCUMENT_VERSION}.'
        )
    node_count, text_length = _measure_content(content)
    if node_count > MAX_DOCUMENT_NODES:
        errors.append(f'Document exceeds {MAX_DOCUMENT_NODES} nodes.')
    if text_length > MAX_DOCUMENT_TEXT_CHARS:
        errors.append(
            f'Document exceeds {MAX_DOCUMENT_TEXT_CHARS} text characters.'
        )
    nodes = content.get('content')
    if not isinstance(nodes, list) or not nodes:
        errors.append('Root content must be a non-empty list.')
    else:
        for index, node in enumerate(nodes):
            _validate_node(
                node,
                f'content[{index}]',
                errors,
                allowed_types={
                    'paragraph',
                    'heading',
                    'bullet_list',
                    'ordered_list',
                    'table',
                },
            )
    if errors:
        raise InvalidDocumentContent(errors)
    return content


def _measure_content(node):
    if not isinstance(node, dict):
        return 0, 0
    node_count = 1
    text = node.get('text')
    text_length = len(text) if isinstance(text, str) else 0
    for child in node.get('content', []):
        child_count, child_text_length = _measure_content(child)
        node_count += child_count
        text_length += child_text_length
    return node_count, text_length


def _validate_node(node, path, errors, *, allowed_types):
    if not isinstance(node, dict):
        errors.append(f'{path} must be an object.')
        return
    node_type = node.get('type')
    if node_type not in allowed_types:
        errors.append(f'{path}.type is unsupported.')
        return

    if node_type == 'text':
        if not isinstance(node.get('text'), str):
            errors.append(f'{path}.text must be a string.')
        marks = node.get('marks', [])
        if (
            not isinstance(marks, list)
            or any(mark not in ALLOWED_MARKS for mark in marks)
            or len(marks) != len(set(marks))
        ):
            errors.append(f'{path}.marks contains unsupported values.')
        return

    attrs = node.get('attrs', {})
    if not isinstance(attrs, dict):
        errors.append(f'{path}.attrs must be an object.')
    elif node_type == 'heading' and attrs.get('level') not in {1, 2, 3, 4}:
        errors.append(f'{path}.attrs.level must be between 1 and 4.')

    children = node.get('content', [])
    if not isinstance(children, list):
        errors.append(f'{path}.content must be a list.')
        return
    child_types = {
        'paragraph': INLINE_NODE_TYPES,
        'heading': INLINE_NODE_TYPES,
        'bullet_list': {'list_item'},
        'ordered_list': {'list_item'},
        'list_item': {
            'paragraph',
            'bullet_list',
            'ordered_list',
        },
        'table': {'table_row'},
        'table_row': {'table_cell'},
        'table_cell': {
            'paragraph',
            'bullet_list',
            'ordered_list',
        },
    }[node_type]
    for index, child in enumerate(children):
        _validate_node(
            child,
            f'{path}.content[{index}]',
            errors,
            allowed_types=child_types,
        )


def render_content(content):
    validate_content(content)
    html = ''.join(_render_node(node) for node in content['content'])
    sanitized_html = bleach.clean(
        html,
        tags=ALLOWED_HTML_TAGS,
        attributes=ALLOWED_HTML_ATTRIBUTES,
        protocols=[],
        strip=True,
    )
    text = '\n'.join(
        line.strip()
        for line in _extract_text(content).splitlines()
        if line.strip()
    )
    return sanitized_html, text


def _render_node(node):
    node_type = node['type']
    if node_type == 'text':
        rendered = escape(node['text'])
        for mark in node.get('marks', []):
            tag = {'bold': 'strong', 'italic': 'em', 'underline': 'u'}[mark]
            rendered = f'<{tag}>{rendered}</{tag}>'
        return rendered

    children = ''.join(_render_node(child) for child in node.get('content', []))
    if node_type == 'heading':
        level = node.get('attrs', {}).get('level', 2)
        return f'<h{level}>{children}</h{level}>'
    tags = {
        'paragraph': 'p',
        'bullet_list': 'ul',
        'ordered_list': 'ol',
        'list_item': 'li',
        'table': 'table',
        'table_row': 'tr',
        'table_cell': 'td',
    }
    tag = tags[node_type]
    return f'<{tag}>{children}</{tag}>'


def _extract_text(node):
    node_type = node.get('type')
    if node_type == 'text':
        return node.get('text', '')
    children = node.get('content', [])
    if node_type in {'paragraph', 'heading', 'table_cell'}:
        return ''.join(_extract_text(child) for child in children)
    if node_type == 'bullet_list':
        return '\n'.join(
            f'- {_extract_text(child).strip()}'
            for child in children
        )
    if node_type == 'ordered_list':
        return '\n'.join(
            f'{index}. {_extract_text(child).strip()}'
            for index, child in enumerate(children, start=1)
        )
    if node_type == 'table_row':
        return '\t'.join(_extract_text(child).strip() for child in children)
    return '\n'.join(_extract_text(child) for child in children)
