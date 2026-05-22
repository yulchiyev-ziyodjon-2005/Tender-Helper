from rest_framework import serializers

from .models import TenderDocumentChunk, TenderLot


class TenderDocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderDocumentChunk
        fields = ['id', 'file_name', 'chunk_index', 'raw_text', 'created_at']
        read_only_fields = ['id', 'created_at']


class TenderLotSerializer(serializers.ModelSerializer):
    chunks_count = serializers.IntegerField(source='chunks.count', read_only=True)

    class Meta:
        model = TenderLot
        fields = [
            'id',
            'lot_number',
            'platform_source',
            'title',
            'buyer_name',
            'start_price',
            'zakalat_amount',
            'region',
            'category',
            'posted_date',
            'deadline',
            'status',
            'raw_portal_url',
            'chunks_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'chunks_count']


class TenderLotDetailSerializer(TenderLotSerializer):
    chunks = TenderDocumentChunkSerializer(many=True, read_only=True)

    class Meta(TenderLotSerializer.Meta):
        fields = TenderLotSerializer.Meta.fields + ['chunks']


class ManualTenderSerializer(serializers.Serializer):
    title = serializers.CharField()
    tender_text = serializers.CharField()
    buyer_name = serializers.CharField(required=False, allow_blank=True, default='')
    start_price = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
        required=False,
        default=0,
    )
    zakalat_amount = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
        required=False,
        default=0,
    )
    region = serializers.CharField(required=False, allow_blank=True, default='')
    category = serializers.CharField(required=False, allow_blank=True, default='manual')
    deadline = serializers.DateTimeField(required=False)
