from rest_framework import serializers

from controlplane.constants import AdminCapability
from subscriptions.constants import Feature
from subscriptions.models import CompanySubscription


class AdminStepUpSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    mfa_code = serializers.CharField(
        write_only=True,
        min_length=6,
        max_length=12,
    )


class AdminActionSerializer(serializers.Serializer):
    reason = serializers.CharField(min_length=10, max_length=1000)
    idempotency_key = serializers.CharField(min_length=8, max_length=100)
    expected_version = serializers.CharField(max_length=100)
    confirmed = serializers.BooleanField()

    def validate_confirmed(self, value):
        if not value:
            raise serializers.ValidationError(
                'Explicit confirmation is required.'
            )
        return value


class PIIRevealSerializer(serializers.Serializer):
    reason = serializers.CharField(min_length=10, max_length=1000)


class UserStatusActionSerializer(AdminActionSerializer):
    action = serializers.ChoiceField(choices=('block', 'unblock', 'revoke'))


class FeatureFlagActionSerializer(AdminActionSerializer):
    is_enabled = serializers.BooleanField()


class SubscriptionChangeFieldsSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=('activate', 'upgrade', 'downgrade', 'pause', 'cancel', 'extend'),
    )
    plan_code = serializers.SlugField(required=False)
    period_end = serializers.DateTimeField(required=False)
    effective_at = serializers.DateTimeField(required=False)
    expected_version = serializers.CharField(max_length=100)

    def validate(self, attrs):
        if attrs['action'] in {'activate', 'upgrade', 'downgrade'}:
            if not attrs.get('plan_code'):
                raise serializers.ValidationError({
                    'plan_code': 'This action requires plan_code.',
                })
        if attrs['action'] == 'extend' and not attrs.get('period_end'):
            raise serializers.ValidationError({
                'period_end': 'Extend requires period_end.',
            })
        if (
            attrs.get('effective_at')
            and attrs.get('period_end')
            and attrs['period_end'] <= attrs['effective_at']
        ):
            raise serializers.ValidationError({
                'period_end': 'Period end must follow effective_at.',
            })
        return attrs


class SubscriptionActionPreviewSerializer(SubscriptionChangeFieldsSerializer):
    pass


class SubscriptionActionSerializer(
    AdminActionSerializer,
    SubscriptionChangeFieldsSerializer,
):
    def validate(self, attrs):
        return SubscriptionChangeFieldsSerializer.validate(self, attrs)


class PlanChangeFieldsSerializer(serializers.Serializer):
    features = serializers.ListField(
        child=serializers.ChoiceField(choices=Feature.ALL),
        required=False,
    )
    limits = serializers.JSONField(required=False)
    price_uzs = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
        allow_null=True,
        required=False,
    )
    is_active = serializers.BooleanField(required=False)
    is_public = serializers.BooleanField(required=False)

    def validate(self, attrs):
        editable = {
            'features',
            'limits',
            'price_uzs',
            'is_active',
            'is_public',
        }
        if not editable.intersection(attrs):
            raise serializers.ValidationError(
                'At least one plan field must be supplied.'
            )
        return attrs


class PlanPreviewSerializer(PlanChangeFieldsSerializer):
    pass


class PlanUpdateSerializer(AdminActionSerializer, PlanChangeFieldsSerializer):
    def validate(self, attrs):
        return PlanChangeFieldsSerializer.validate(self, attrs)


class TemplatePublishActionSerializer(AdminActionSerializer):
    publish = serializers.BooleanField()


class CapabilityAssignmentSerializer(AdminActionSerializer):
    capabilities = serializers.ListField(
        child=serializers.ChoiceField(choices=AdminCapability.ALL),
        allow_empty=False,
    )
    is_active = serializers.BooleanField(default=True)


class SubscriptionStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=CompanySubscription.Status.choices)


class MaintenanceBannerActionSerializer(AdminActionSerializer):
    enabled = serializers.BooleanField()
    message = serializers.CharField(
        max_length=500,
        allow_blank=True,
        required=False,
        default='',
    )
    severity = serializers.ChoiceField(
        choices=('info', 'warning', 'critical'),
        default='warning',
    )
    starts_at = serializers.DateTimeField(required=False, allow_null=True)
    ends_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['enabled'] and not attrs.get('message', '').strip():
            raise serializers.ValidationError({
                'message': 'Enabled maintenance banner requires a message.',
            })
        if (
            attrs.get('starts_at')
            and attrs.get('ends_at')
            and attrs['ends_at'] <= attrs['starts_at']
        ):
            raise serializers.ValidationError({
                'ends_at': 'ends_at must follow starts_at.',
            })
        return attrs
