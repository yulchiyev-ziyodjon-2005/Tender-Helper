import operator
from functools import reduce

from django.db.models import Q
from django.utils.text import smart_split, unescape_string_literal

SEARCH_FIELDS = (
    'title',
    'buyer_name',
    'lot_number',
    'category',
)
MAX_SEARCH_QUERY_LENGTH = 200


class SearchQueryTooLong(ValueError):
    pass


def search_terms(query):
    query = str(query or '')
    if len(query) > MAX_SEARCH_QUERY_LENGTH:
        raise SearchQueryTooLong(
            f'Search query cannot exceed {MAX_SEARCH_QUERY_LENGTH} characters.'
        )
    terms = []
    for term in smart_split(query):
        term = term.strip(',')
        if term.startswith(('"', "'")) and term[0] == term[-1]:
            terms.append(unescape_string_literal(term))
            continue
        terms.extend(
            part.strip()
            for part in term.split(',')
            if part.strip()
        )
    return terms


def apply_tender_search(queryset, query):
    terms = search_terms(query)
    for term in terms:
        condition = reduce(
            operator.or_,
            (Q(**{f'{field}__icontains': term}) for field in SEARCH_FIELDS),
        )
        queryset = queryset.filter(condition)
    return queryset
