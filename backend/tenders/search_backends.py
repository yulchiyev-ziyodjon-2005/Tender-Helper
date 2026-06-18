from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter

from tenders.services.search import (
    SearchQueryTooLong,
    apply_tender_search,
)


class TenderSearchFilter(SearchFilter):
    def filter_queryset(self, request, queryset, view):
        try:
            return apply_tender_search(
                queryset,
                request.query_params.get(self.search_param, ''),
            )
        except SearchQueryTooLong as exc:
            raise ValidationError({'search': str(exc)}) from exc
