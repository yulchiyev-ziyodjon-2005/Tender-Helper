import django_filters

from .models import TenderLot


class TenderLotFilter(django_filters.FilterSet):
    region = django_filters.CharFilter(lookup_expr='iexact')
    category = django_filters.CharFilter(lookup_expr='iexact')
    min_price = django_filters.NumberFilter(field_name='start_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='start_price', lookup_expr='lte')
    deadline_before = django_filters.DateTimeFilter(field_name='deadline', lookup_expr='lte')
    deadline_after = django_filters.DateTimeFilter(field_name='deadline', lookup_expr='gte')
    posted_after = django_filters.DateTimeFilter(field_name='posted_date', lookup_expr='gte')
    posted_before = django_filters.DateTimeFilter(field_name='posted_date', lookup_expr='lte')

    class Meta:
        model = TenderLot
        fields = [
            'region',
            'category',
            'platform_source',
            'status',
            'min_price',
            'max_price',
            'deadline_before',
            'deadline_after',
            'posted_after',
            'posted_before',
        ]
