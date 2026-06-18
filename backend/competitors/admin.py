from django.contrib import admin

from competitors.models import (
    CompetitorAnalytics,
    CompetitorAnalyticsSource,
    CompetitorDataQualityIssue,
    TenderAward,
    TenderBid,
    TenderParticipant,
)


class ReadOnlyAnalyticsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TenderParticipant)
class TenderParticipantAdmin(admin.ModelAdmin):
    list_display = (
        'normalized_name',
        'stir',
        'tender_lot',
        'source_reference',
        'updated_at',
    )
    search_fields = (
        'normalized_name',
        'stir',
        'tender_lot__lot_number',
    )
    list_select_related = ('tender_lot',)


@admin.register(TenderBid)
class TenderBidAdmin(admin.ModelAdmin):
    list_display = (
        'participant',
        'sequence',
        'amount',
        'currency',
        'is_valid',
        'submitted_at',
    )
    list_filter = ('currency', 'is_valid')
    list_select_related = ('participant',)


@admin.register(TenderAward)
class TenderAwardAdmin(admin.ModelAdmin):
    list_display = (
        'tender_lot',
        'winner',
        'winning_bid',
        'awarded_at',
        'is_verified',
    )
    list_filter = ('is_verified', 'awarded_at')
    search_fields = (
        'tender_lot__lot_number',
        'winner__normalized_name',
        'winner__stir',
    )
    list_select_related = ('tender_lot', 'winner', 'winning_bid')


@admin.register(CompetitorDataQualityIssue)
class CompetitorDataQualityIssueAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'severity',
        'tender_lot',
        'resolved_at',
        'updated_at',
    )
    list_filter = ('code', 'severity', 'resolved_at')
    search_fields = ('tender_lot__lot_number', 'fingerprint')
    readonly_fields = ('fingerprint', 'details', 'created_at', 'updated_at')
    list_select_related = ('tender_lot',)


@admin.register(CompetitorAnalytics)
class CompetitorAnalyticsAdmin(ReadOnlyAnalyticsAdmin):
    list_display = (
        'scope_type',
        'category',
        'competitor_name',
        'competitor_stir',
        'rank',
        'total_participations',
        'total_wins',
        'win_rate',
        'source_count',
        'calculated_at',
    )
    list_filter = ('scope_type', 'category', 'period_end')
    search_fields = ('competitor_name', 'competitor_stir', 'identity_key')
    list_select_related = ('tender_lot',)


@admin.register(CompetitorAnalyticsSource)
class CompetitorAnalyticsSourceAdmin(ReadOnlyAnalyticsAdmin):
    list_display = (
        'analytics',
        'participant',
        'award',
        'was_winner',
        'bid_amount',
        'discount_percentage',
    )
    list_filter = ('was_winner',)
    list_select_related = ('analytics', 'participant', 'award', 'bid')
