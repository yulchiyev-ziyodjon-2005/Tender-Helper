from django.contrib import admin

from .models import AITenderAnalysis, SmartCalculator


@admin.register(AITenderAnalysis)
class AITenderAnalysisAdmin(admin.ModelAdmin):
    list_display = ('company', 'tender_lot', 'analysis_status', 'eligibility_score', 'created_at')
    list_filter = ('analysis_status', 'created_at')
    search_fields = ('company__company_name', 'tender_lot__lot_number', 'tender_lot__title')
    ordering = ('-created_at',)


@admin.register(SmartCalculator)
class SmartCalculatorAdmin(admin.ModelAdmin):
    list_display = ('analysis', 'min_safe_price', 'recommended_price', 'net_profit', 'updated_at')
    search_fields = ('analysis__company__company_name', 'analysis__tender_lot__lot_number')
