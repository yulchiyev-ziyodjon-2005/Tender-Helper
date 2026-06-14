from django.contrib import admin

from .models import CompanyProfile, CompanyRegistryDraft


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = (
        'company_name',
        'stir',
        'registry_status',
        'registry_source',
        'company_type',
        'industry',
        'current_tariff',
        'created_at',
    )
    list_filter = (
        'registry_status',
        'registry_source',
        'company_type',
        'industry',
        'current_tariff',
        'has_vat',
        'stir_skipped',
    )
    search_fields = ('company_name', 'stir', 'user__phone_number', 'user__email')
    ordering = ('-created_at',)


@admin.register(CompanyRegistryDraft)
class CompanyRegistryDraftAdmin(admin.ModelAdmin):
    list_display = (
        'stir',
        'provider',
        'source',
        'status',
        'cache_hit',
        'created_at',
        'expires_at',
    )
    list_filter = ('provider', 'source', 'status', 'cache_hit')
    search_fields = ('stir', 'user__phone_number', 'user__email')
    readonly_fields = (
        'user',
        'profile',
        'stir',
        'normalized_data',
        'confirmed_data',
        'raw_payload',
        'provider',
        'source',
        'lookup_metadata',
        'status',
        'error_code',
        'error_message',
        'cache_hit',
        'expires_at',
        'confirmed_at',
        'created_at',
        'updated_at',
    )
    ordering = ('-created_at',)
