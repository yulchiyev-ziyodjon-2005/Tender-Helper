import uuid
from datetime import timedelta

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import TenderLotFilter
from .models import TenderDocumentChunk, TenderLot
from .serializers import (
    ManualTenderSerializer,
    TenderLotDetailSerializer,
    TenderLotSerializer,
)


class TenderListView(generics.ListAPIView):
    serializer_class = TenderLotSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TenderLotFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'buyer_name', 'lot_number']
    ordering_fields = ['posted_date', 'deadline', 'start_price']
    ordering = ['-posted_date']

    def get_queryset(self):
        return TenderLot.objects.filter(status=TenderLot.Status.ACTIVE)


class TenderDetailView(generics.RetrieveAPIView):
    queryset = TenderLot.objects.all()
    serializer_class = TenderLotDetailSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manual_tender_view(request):
    """
    POST /api/v1/tenders/manual/
    Foydalanuvchi qo'lda kiritgan tender matnini lot sifatida saqlash.
    """
    serializer = ManualTenderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    tender = TenderLot.objects.create(
        lot_number=f"MANUAL-{uuid.uuid4().hex[:10].upper()}",
        platform_source=TenderLot.PlatformSource.MANUAL,
        title=data['title'],
        buyer_name=data.get('buyer_name', ''),
        start_price=data.get('start_price', 0),
        zakalat_amount=data.get('zakalat_amount', 0),
        region=data.get('region', ''),
        category=data.get('category', 'manual'),
        posted_date=timezone.now(),
        deadline=data.get('deadline') or (timezone.now() + timedelta(days=7)),
        status=TenderLot.Status.ACTIVE,
    )
    TenderDocumentChunk.objects.create(
        tender_lot=tender,
        file_name='manual-input.txt',
        chunk_index=0,
        raw_text=data['tender_text'],
    )

    return Response(TenderLotDetailSerializer(tender).data, status=status.HTTP_201_CREATED)
