from rest_framework import serializers

from .models import TenderDocumentChunk, TenderLot


class TenderDocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderDocumentChunk
        fields = ['id', 'file_name', 'chunk_index', 'raw_text', 'created_at']
        read_only_fields = ['id', 'created_at']


class TenderLotSerializer(serializers.ModelSerializer):
    chunks_count = serializers.SerializerMethodField()
    source = serializers.SlugRelatedField(
        slug_field='code',
        read_only=True,
    )

    class Meta:
        model = TenderLot
        fields = [
            'id',
            'source',
            'external_id',
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

    def get_chunks_count(self, obj):
        counted_chunks = getattr(obj, 'counted_chunks', None)
        if counted_chunks is not None:
            return len(counted_chunks)
        prefetched = getattr(obj, '_prefetched_objects_cache', {}).get('chunks')
        if prefetched is not None:
            return len(prefetched)
        return obj.chunks.count()


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
