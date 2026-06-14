from rest_framework import serializers

from subscriptions.constants import Feature
from subscriptions.models import (
    CompanySubscription,
    SubscriptionPlan,
    UsageRecord,
)


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id',
            'code',
            'name',
            'description',
            'rank',
            'features',
            'limits',
            'price_uzs',
            'currency',
            'billing_period',
        ]
        read_only_fields = fields


class CompanySubscriptionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)

    class Meta:
        model = CompanySubscription
        fields = [
            'id',
            'company_id',
            'plan',
            'status',
            'source',
            'starts_at',
            'trial_ends_at',
            'current_period_start',
            'current_period_end',
            'cancel_at_period_end',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class UsageRecordSerializer(serializers.ModelSerializer):
    remaining = serializers.SerializerMethodField()

    class Meta:
        model = UsageRecord
        fields = [
            'metric',
            'period_start',
            'period_end',
            'used',
            'limit_snapshot',
            'remaining',
            'updated_at',
        ]
        read_only_fields = fields

    def get_remaining(self, obj):
        if obj.limit_snapshot is None:
            return None
        return max(obj.limit_snapshot - obj.used, 0)


class EntitlementSerializer(serializers.Serializer):
    feature = serializers.ChoiceField(choices=Feature.ALL)
    allowed = serializers.BooleanField()
    plan = serializers.CharField()
    role = serializers.CharField()
    required_plan = serializers.CharField()
    requires_stir = serializers.BooleanField()
    denial_code = serializers.CharField(allow_null=True)


class CheckoutSerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=False)
    plan_code = serializers.SlugField()

    def validate_plan_code(self, value):
        if not SubscriptionPlan.objects.filter(
            code=value,
            is_active=True,
            is_public=True,
        ).exists():
            raise serializers.ValidationError('Unknown or unavailable plan.')
        return value
