from django.contrib import admin

from subscriptions.models import (
    CompanySubscription,
    SubscriptionPlan,
    UsageRecord,
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
    )
    list_filter = ('status', 'source', 'plan')
    search_fields = (
        'company__company_name',
        'company__stir',
        'external_reference',
    )
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)


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
