from rest_framework import serializers

from .models import (
    AITenderAnalysis,
    AnalysisFinding,
    AnalysisRun,
    LegalKnowledgeSource,
    ModelInvocation,
    SmartCalculator,
)


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


class AnalysisFindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisFinding
        fields = [
            'id',
            'finding_type',
            'title',
            'description',
            'risk_factor',
            'rating_score',
            'compliance_status',
            'citations',
            'created_at',
        ]
        read_only_fields = fields


class ModelInvocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelInvocation
        fields = [
            'id',
            'provider',
            'model_name',
            'prompt_version',
            'token_count',
            'prompt_tokens',
            'output_tokens',
            'calculated_cost',
            'latency_ms',
            'status',
            'error_code',
            'created_at',
        ]
        read_only_fields = fields


class AnalysisStatusSerializer(serializers.ModelSerializer):
    analysis_id = serializers.UUIDField(source='analysis.id', read_only=True)
    analysis_status = serializers.CharField(
        source='analysis.analysis_status',
        read_only=True,
    )
    eligibility_score = serializers.IntegerField(
        source='analysis.eligibility_score',
        read_only=True,
    )
    findings = AnalysisFindingSerializer(many=True, read_only=True)
    model_invocations = ModelInvocationSerializer(many=True, read_only=True)

    class Meta:
        model = AnalysisRun
        fields = [
            'id',
            'analysis_id',
            'status',
            'analysis_status',
            'progress_percent',
            'eligibility_score',
            'started_at',
            'completed_at',
            'error_code',
            'error_message',
            'findings',
            'model_invocations',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class StartAnalysisResponseSerializer(serializers.ModelSerializer):
    analysis_id = serializers.UUIDField(source='analysis.id', read_only=True)
    status_url = serializers.SerializerMethodField()
    result_url = serializers.SerializerMethodField()

    class Meta:
        model = AnalysisRun
        fields = [
            'id',
            'analysis_id',
            'status',
            'progress_percent',
            'status_url',
            'result_url',
            'created_at',
        ]
        read_only_fields = fields

    def get_status_url(self, obj):
        return f'/analysis/{obj.id}/status/'

    def get_result_url(self, obj):
        return f'/analysis/{obj.id}/result/'


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


class LegalKnowledgeSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalKnowledgeSource
        fields = [
            'code',
            'name',
            'authority_level',
            'base_url',
            'allowed_domains',
            'source_rank',
            'requires_effective_date_check',
            'requires_manual_review',
            'is_active',
            'metadata',
            'updated_at',
        ]
        read_only_fields = fields
