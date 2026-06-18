from django.contrib import admin

from subscriptions.models import (
    CompanySubscription,
    NotificationLog,
    PaymentTransaction,
    SubscriptionPlan,
    UsageRecord,
    WebhookEvent,
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'rank',
        'billing_period',
        'price_uzs',
        'is_active',
        'is_public',
    )
    list_filter = ('billing_period', 'is_active', 'is_public')
    search_fields = ('code', 'name')
    ordering = ('rank', 'code')


@admin.register(CompanySubscription)
class CompanySubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'company',
        'plan',
        'status',
        'source',
        'current_period_start',
        'current_period_end',
        'scheduled_plan',
        'scheduled_change_at',
        'sms_allowed_monthly',
        'sms_sent_this_month',
        'daily_sms_cap',
    )
    list_filter = ('status', 'source', 'plan')
    search_fields = (
        'company__company_name',
        'company__stir',
        'external_reference',
    )
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'team',
        'tender',
        'status',
        'sent_at',
        'provider_message_id',
    )
    list_filter = ('status', 'sent_at')
    search_fields = (
        'user__phone_number',
        'user__email',
        'tender__tender_id',
        'provider_message_id',
    )
    readonly_fields = ('sent_at',)
    ordering = ('-sent_at',)


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'merchant_trans_id',
        'company',
        'plan',
        'provider',
        'status',
        'amount',
        'currency',
        'created_at',
    )
    list_filter = ('provider', 'status', 'billing_period', 'currency')
    search_fields = (
        'merchant_trans_id',
        'provider_transaction_id',
        'provider_payment_id',
        'company__company_name',
        'company__stir',
    )
    readonly_fields = (
        'public_id',
        'created_at',
        'updated_at',
        'prepared_at',
        'paid_at',
        'canceled_at',
    )
    ordering = ('-created_at',)


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = (
        'provider',
        'event_type',
        'provider_event_id',
        'action',
        'status',
        'received_at',
    )
    list_filter = ('provider', 'event_type', 'action', 'status')
    search_fields = (
        'provider_event_id',
        'transaction__merchant_trans_id',
        'error_code',
    )
    readonly_fields = ('received_at', 'processed_at')
    ordering = ('-received_at',)


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = (
        'company',
        'metric',
        'used',
        'limit_snapshot',
        'period_start',
        'period_end',
    )
    list_filter = ('metric',)
    search_fields = ('company__company_name', 'company__stir')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-period_start', 'metric')
