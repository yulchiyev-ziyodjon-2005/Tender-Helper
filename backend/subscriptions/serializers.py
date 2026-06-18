from rest_framework import serializers

from subscriptions.constants import Feature
from subscriptions.models import (
    CompanySubscription,
    PaymentTransaction,
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
            'scheduled_plan_id',
            'scheduled_change_at',
            'scheduled_period_end',
            'sms_allowed_monthly',
            'sms_sent_this_month',
            'daily_sms_cap',
            'sms_counter_period_start',
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
    provider = serializers.ChoiceField(
        choices=PaymentTransaction.Provider.choices,
        default=PaymentTransaction.Provider.CLICK,
    )

    def validate_plan_code(self, value):
        if not SubscriptionPlan.objects.filter(
            code=value,
            is_active=True,
            is_public=True,
        ).exists():
            raise serializers.ValidationError('Unknown or unavailable plan.')
        return value


class PaymentTransactionSerializer(serializers.ModelSerializer):
    plan = SubscriptionPlanSerializer(read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = [
            'public_id',
            'company_id',
            'plan',
            'provider',
            'status',
            'merchant_trans_id',
            'amount',
            'currency',
            'billing_period',
            'provider_transaction_id',
            'provider_payment_id',
            'prepared_at',
            'paid_at',
            'canceled_at',
            'error_code',
            'error_message',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
