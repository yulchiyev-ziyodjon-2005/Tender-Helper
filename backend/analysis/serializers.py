from rest_framework import serializers

from .models import AITenderAnalysis, SmartCalculator


class StartAnalysisSerializer(serializers.Serializer):
    lot_id = serializers.UUIDField()
    company_id = serializers.UUIDField(required=False)
    additional_text = serializers.CharField(required=False, allow_blank=True, default='')


class AITenderAnalysisSerializer(serializers.ModelSerializer):
    tender_lot = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()

    class Meta:
        model = AITenderAnalysis
        fields = [
            'id',
            'company',
            'tender_lot',
            'analysis_status',
            'eligibility_score',
            'summary_text',
            'missing_documents',
            'red_flags',
            'requirements',
            'standards',
            'decision',
            'error_message',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_tender_lot(self, obj):
        return {
            'id': obj.tender_lot_id,
            'lot_number': obj.tender_lot.lot_number,
            'title': obj.tender_lot.title,
            'start_price': obj.tender_lot.start_price,
            'deadline': obj.tender_lot.deadline,
        }

    def get_company(self, obj):
        return {
            'id': obj.company_id,
            'company_name': obj.company.company_name,
            'current_tariff': obj.company.current_tariff,
        }


class AnalysisStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AITenderAnalysis
        fields = ['id', 'analysis_status', 'eligibility_score', 'error_message', 'updated_at']
        read_only_fields = fields


class CalculatorInputSerializer(serializers.Serializer):
    raw_material_cost = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=0)
    logistics_cost = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=0)
    labor_cost = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=0)
    other_expenses = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=0)


class SmartCalculatorSerializer(serializers.ModelSerializer):
    tannarx = serializers.SerializerMethodField()

    class Meta:
        model = SmartCalculator
        fields = [
            'id',
            'raw_material_cost',
            'logistics_cost',
            'labor_cost',
            'other_expenses',
            'tannarx',
            'calculated_vat',
            'calculated_operator_fee',
            'calculated_zakalat',
            'min_safe_price',
            'recommended_price',
            'net_profit',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_tannarx(self, obj):
        return (
            obj.raw_material_cost
            + obj.logistics_cost
            + obj.labor_cost
            + obj.other_expenses
        )
