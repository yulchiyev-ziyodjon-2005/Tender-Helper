from django.contrib import admin

from .models import TenderDocumentChunk, TenderLot, TenderSource


@admin.register(TenderSource)
class TenderSourceAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'base_url', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('code', 'name', 'base_url')


class TenderDocumentChunkInline(admin.TabularInline):
    model = TenderDocumentChunk
    extra = 0
    fields = ('file_name', 'chunk_index')
    readonly_fields = ('file_name', 'chunk_index')


@admin.register(TenderLot)
class TenderLotAdmin(admin.ModelAdmin):
    list_display = (
        'lot_number',
        'source',
        'external_id',
        'title',
        'platform_source',
        'start_price',
        'deadline',
        'status',
    )
    list_filter = ('source', 'platform_source', 'status', 'region', 'category')
    search_fields = ('external_id', 'lot_number', 'title', 'buyer_name')
    ordering = ('-posted_date',)
    inlines = [TenderDocumentChunkInline]


@admin.register(TenderDocumentChunk)
class TenderDocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('tender_lot', 'file_name', 'chunk_index', 'created_at')
    search_fields = ('tender_lot__lot_number', 'file_name', 'raw_text')
