import json
import logging

import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from companies.models import CompanyProfile
from subscriptions.models import UsageRecord
from subscriptions.services.usage import consume_usage
from tenders.models import TenderLot
from .models import AITenderAnalysis, SmartCalculator
from .serializers import (
    AITenderAnalysisSerializer,
    AnalysisStatusSerializer,
    CalculatorInputSerializer,
    SmartCalculatorSerializer,
    StartAnalysisSerializer,
)

logger = logging.getLogger(__name__)


def _current_company(user, company_id=None):
    companies = CompanyProfile.objects.filter(user=user)
    if company_id:
        return get_object_or_404(companies, id=company_id)
    return companies.order_by('-created_at').first()


def _collect_tender_text(tender, additional_text=''):
    chunks = tender.chunks.order_by('chunk_index').values_list('raw_text', flat=True)
    text = '\n'.join(chunks)
    if additional_text:
        text = f"{text}\n{additional_text}".strip()
    return text or tender.title


def _run_rule_based_analysis(analysis, tender_text):
    """
    Haqiqiy Gemini API (Flash/Pro) REST API orqali.
    """
    tender = analysis.tender_lot
    company = analysis.company
    
    prompt = f"""
    Siz professional tender va davlat xaridlari bo'yicha yurist va tahlilchisiz.
    Quyida tender loti haqida ma'lumot va uning texnik topshiriqlari keltirilgan.
    Shuningdek, ushbu tenderda ishtirok etmoqchi bo'lgan kompaniya ma'lumotlari ham bor.
    Sizning vazifangiz tenderni tahlil qilish va qat'iy JSON formatida javob berish.

    KOMPANIYA:
    Nomi: {company.company_name}
    Tashkiliy shakli: {company.company_type}
    Sohasi: {company.industry}
    QQS to'lovchimi: {'Ha' if company.has_vat else 'Yoq'}

    TENDER:
    Sarlavha: {tender.title}
    Buyurtmachi: {tender.buyer_name}
    Narxi: {tender.start_price} so'm
    Matn:
    {tender_text[:10000]}

    Iltimos, faqat quyidagi JSON strukturasida javob qaytaring (hech qanday markdown yoki qo'shimcha matnsiz, faqat JSON formatida):
    {{
        "eligibility_score": 85,
        "summary_text": "<qisqa xulosa, maks 300 belgi>",
        "missing_documents": [
            {{"name": "Hujjat nomi", "reason": "Nima uchun kerak", "category": "common"}}
        ],
        "red_flags": [
            {{"level": "blocker yoki warning", "title": "Sarlavha", "reason": "Izoh", "recommendation": "Maslahat"}}
        ],
        "standards": [
            {{"name": "ISO/GOST", "meaning": "Ma'nosi", "action": "Nima qilish kerak"}}
        ],
        "requirements": [
            {{"original": "Asl matn", "plain": "Sodda tili", "action": "Bajarilishi kerak"}}
        ],
        "decision": {{
            "fit_percent": 85,
            "risk_percent": 15,
            "recommendation": "Tavsiya",
            "next_actions": ["qadam 1", "qadam 2"],
            "disclaimer": "Ushbu natija huquqiy maslahat emas."
        }}
    }}
    """
    
    try:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise RuntimeError('Gemini API key is not configured')
        url = (
            'https://generativelanguage.googleapis.com/v1beta/models/'
            f'{settings.GEMINI_MODEL}:generateContent?key={api_key}'
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }
        
        session = requests.Session()
        session.trust_env = False
        response = session.post(
            url, 
            json=payload, 
            headers={'Content-Type': 'application/json'}, 
            timeout=settings.GEMINI_TIMEOUT
        )
        response.raise_for_status()
        res_json = response.json()
        
        result_str = res_json['candidates'][0]['content']['parts'][0]['text']
        
        # Fallback agar model markdown bilan o'rab qoysa
        if result_str.startswith("```json"):
            result_str = result_str[7:-3].strip()
        elif result_str.startswith("```"):
            result_str = result_str[3:-3].strip()
            
        data = json.loads(result_str)
        
        analysis.analysis_status = AITenderAnalysis.Status.COMPLETED
        analysis.eligibility_score = data.get('eligibility_score', 50)
        analysis.summary_text = data.get('summary_text', '')
        analysis.missing_documents = data.get('missing_documents', [])
        analysis.red_flags = data.get('red_flags', [])
        analysis.requirements = data.get('requirements', [])
        analysis.standards = data.get('standards', [])
        analysis.decision = data.get('decision', {})
        
    except Exception:
        logger.exception('AI analysis provider failed for analysis %s', analysis.id)
        analysis.analysis_status = AITenderAnalysis.Status.FAILED
        analysis.error_message = 'AI provider is temporarily unavailable'

    analysis.save()
    return analysis



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_analysis_view(request):
    serializer = StartAnalysisSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    company = _current_company(request.user, data.get('company_id'))
    if company is None:
        return Response(
            {
                'error': 'profile_required',
                'message': 'AI tahlil uchun avval kompaniya profilini yarating',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    tender = get_object_or_404(TenderLot, id=data['lot_id'])
    consume_usage(company, UsageRecord.Metric.AI_ANALYSIS)
    analysis = AITenderAnalysis.objects.create(
        company=company,
        tender_lot=tender,
        analysis_status=AITenderAnalysis.Status.PROCESSING_DOCS,
    )

    analysis.analysis_status = AITenderAnalysis.Status.CHECKING_COMPLIANCE
    analysis.save(update_fields=['analysis_status', 'updated_at'])
    tender_text = _collect_tender_text(tender, data.get('additional_text', ''))
    analysis.analysis_status = AITenderAnalysis.Status.DETECTING_RED_FLAGS
    analysis.save(update_fields=['analysis_status', 'updated_at'])
    analysis = _run_rule_based_analysis(analysis, tender_text)

    return Response(AITenderAnalysisSerializer(analysis).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analysis_status_view(request, pk):
    analysis = get_object_or_404(
        AITenderAnalysis.objects.filter(company__user=request.user),
        id=pk,
    )
    return Response(AnalysisStatusSerializer(analysis).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analysis_result_view(request, pk):
    analysis = get_object_or_404(
        AITenderAnalysis.objects.filter(company__user=request.user),
        id=pk,
    )
    return Response(AITenderAnalysisSerializer(analysis).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analysis_history_view(request):
    analyses = AITenderAnalysis.objects.filter(company__user=request.user).select_related(
        'company',
        'tender_lot',
    )
    serializer = AITenderAnalysisSerializer(analyses, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_view(request, pk):
    analysis = get_object_or_404(
        AITenderAnalysis.objects.filter(company__user=request.user),
        id=pk,
    )
    serializer = CalculatorInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    calculator, _ = SmartCalculator.objects.get_or_create(analysis=analysis)
    for field, value in serializer.validated_data.items():
        setattr(calculator, field, value)
    calculator.calculate()
    calculator.save()
    return Response(SmartCalculatorSerializer(calculator).data)
