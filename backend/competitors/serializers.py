from django.conf import settings
from rest_framework import serializers

from competitors.models import CompetitorAnalytics
from competitors.services.identity import normalize_category


class CompetitorAnalyticsSerializer(serializers.ModelSerializer):
    source_lot_ids = serializers.SerializerMethodField()

    class Meta:
        model = CompetitorAnalytics
        fields = [
            'id',
            'scope_type',
            'tender_lot_id',
            'category',
            'competitor_name',
            'competitor_stir',
            'period_start',
            'period_end',
            'rank',
            'total_participations',
            'total_wins',
            'win_rate',
            'average_bid_amount',
            'average_discount_percentage',
            'source_count',
            'source_lot_ids',
            'calculated_at',
        ]
        read_only_fields = fields

    def get_source_lot_ids(self, obj):
        return sorted({
            str(source.award.tender_lot_id)
            for source in obj.sources.all()
        })


class CompetitorQuerySerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=False)
    lot_id = serializers.UUIDField(required=False)
    category = serializers.CharField(max_length=255, required=False)
    period = serializers.ChoiceField(
        choices=tuple(
            f'{days}d' for days in settings.COMPETITOR_PERIOD_DAYS
        ),
        required=False,
        default=(
            '365d'
            if 365 in settings.COMPETITOR_PERIOD_DAYS
            else f'{max(settings.COMPETITOR_PERIOD_DAYS)}d'
        ),
    )
    period_start = serializers.DateField(required=False)
    period_end = serializers.DateField(required=False)

    def validate(self, attrs):
        if bool(attrs.get('lot_id')) == bool(attrs.get('category')):
            raise serializers.ValidationError(
                'Exactly one of lot_id or category is required.'
            )
        if bool(attrs.get('period_start')) != bool(attrs.get('period_end')):
            raise serializers.ValidationError(
                'period_start and period_end must be provided together.'
            )
        if (
            attrs.get('period_start')
            and attrs['period_end'] < attrs['period_start']
        ):
            raise serializers.ValidationError(
                'period_end cannot be before period_start.'
            )
        if attrs.get('category'):
            try:
                attrs['category'] = normalize_category(attrs['category'])
            except ValueError as exc:
                raise serializers.ValidationError({
                    'category': str(exc),
                }) from exc
        return attrs


class CompetitorHistoryQuerySerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=False)
    category = serializers.CharField(max_length=255, required=False)

    def validate_category(self, value):
        try:
            return normalize_category(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc


class CompanyScopeQuerySerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=False)
