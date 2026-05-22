from django.contrib import admin

from .models import CompanyProfile


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'stir', 'company_type', 'industry', 'current_tariff', 'created_at')
    list_filter = ('company_type', 'industry', 'current_tariff', 'has_vat')
    search_fields = ('company_name', 'stir', 'user__phone_number', 'user__email')
    ordering = ('-created_at',)
