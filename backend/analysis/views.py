from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from companies.models import CompanyProfile
from tenders.models import TenderLot
from .models import AITenderAnalysis, SmartCalculator
from .serializers import (
    AITenderAnalysisSerializer,
    AnalysisStatusSerializer,
    CalculatorInputSerializer,
    SmartCalculatorSerializer,
    StartAnalysisSerializer,
)


def _current_company(user, company_id=None):
    queryset = CompanyProfile.objects.filter(user=user)
    if company_id:
        return get_object_or_404(queryset, id=company_id)
    return queryset.order_by('-created_at').first()


def _collect_tender_text(tender, additional_text=''):
    chunks = tender.chunks.order_by('chunk_index').values_list('raw_text', flat=True)
    text = '\n'.join(chunks)
    if additional_text:
        text = f"{text}\n{additional_text}".strip()
    return text or tender.title


def _run_rule_based_analysis(analysis, tender_text):
    """
    MVP fallback tahlil.
    Gemini integratsiyasi ulanmaguncha API oqimini barqaror ishlatadi.
    """
    tender = analysis.tender_lot
    text_lower = tender_text.lower()
    red_flags = []
    requirements = []
    standards = []
    missing_documents = [
        {
            'name': "STIR guvohnomasi yoki ro'yxatdan o'tganlik hujjati",
            'reason': "Deyarli barcha tenderlarda korxona identifikatsiyasi so'raladi",
            'category': 'company_type',
        },
        {
            'name': "Soliq qarzdorligi yo'qligi haqida ma'lumot",
            'reason': "Diskvalifikatsiya xavfini kamaytiradi",
            'category': 'common',
        },
    ]

    days_left = (tender.deadline - timezone.now()).days
    if days_left < 10:
        red_flags.append({
            'level': 'warning',
            'title': 'Tayyorlanish muddati qisqa',
            'reason': f'Ariza topshirishga taxminan {max(days_left, 0)} kun qoldi',
            'recommendation': "Hujjatlar tayyor bo'lmasa, qatnashishdan oldin muddatni baholang",
        })

    if any(word in text_lower for word in ['faqat', 'ekvivalent qabul qilinmaydi', 'brend']):
        red_flags.append({
            'level': 'blocker',
            'title': "Raqobatni cheklashi mumkin bo'lgan shart",
            'reason': "Matnda aniq brend yoki muqobilni cheklovchi iboralar uchradi",
            'recommendation': "Texnik shartlarni huquqshunos yoki soha mutaxassisi bilan tekshiring",
        })

    if any(word in text_lower for word in ['jarima', 'penya']):
        red_flags.append({
            'level': 'warning',
            'title': 'Jarima shartlari bor',
            'reason': "Shartnomada moliyaviy javobgarlik bandlari bo'lishi mumkin",
            'recommendation': "Jarima foizlari va muddatlarini alohida hisoblang",
        })

    for standard in ['ozdst', "o'zdst", 'gost', 'iso']:
        if standard in text_lower:
            standards.append({
                'name': standard.upper(),
                'meaning': "Tender matnida standart talabi aniqlangan",
                'action': "Mahsulot yoki xizmat sertifikatlari mosligini tekshiring",
            })

    requirements.append({
        'original': tender.title,
        'plain': "Tender predmeti bo'yicha yetkazib berish yoki xizmat ko'rsatish talab qilinadi",
        'action': "Texnik topshiriqdagi miqdor, muddat va sifat talablarini tekshiring",
    })

    risk_penalty = min(len(red_flags) * 15, 45)
    score = max(50, 85 - risk_penalty)
    risk_percent = min(20 + risk_penalty, 90)
    recommendation = "Qatnashish mumkin, lekin risklarni tekshiring"
    if any(flag['level'] == 'blocker' for flag in red_flags):
        recommendation = "Ehtiyot bo'ling: bloklovchi risk bor"
    elif score >= 75:
        recommendation = "Qatnashish uchun yaxshi nomzod"

    analysis.analysis_status = AITenderAnalysis.Status.COMPLETED
    analysis.eligibility_score = score
    analysis.summary_text = (
        f"{tender.buyer_name or 'Buyurtmachi'} uchun '{tender.title}' tenderi. "
        f"Boshlang'ich narx: {tender.start_price} so'm. "
        "Bu avtomatik MVP tahlil bo'lib, yakuniy qaror uchun hujjatlarni qayta tekshiring."
    )
    analysis.missing_documents = missing_documents
    analysis.red_flags = red_flags
    analysis.requirements = requirements
    analysis.standards = standards
    analysis.decision = {
        'fit_percent': score,
        'risk_percent': risk_percent,
        'recommendation': recommendation,
        'next_actions': [
            "Tender hujjatlarini to'liq yuklab oling",
            "Kalkulyatorda stop-loss narxini hisoblang",
            "Red flag bandlarini huquqshunos bilan tekshiring",
        ],
        'disclaimer': "Ushbu natija huquqiy maslahat emas.",
    }
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
