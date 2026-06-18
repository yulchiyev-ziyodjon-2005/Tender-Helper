from django.contrib import admin

from documents.models import (
    DocumentAuditEvent,
    DocumentExport,
    GeneratedDocument,
    GeneratedDocumentRevision,
    TenderDocumentTemplate,
)


@admin.register(TenderDocumentTemplate)
class TenderDocumentTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'document_type',
        'language',
        'version',
        'is_active',
        'is_published',
    )
    list_filter = (
        'document_type',
        'language',
        'is_active',
        'is_published',
    )
    search_fields = ('code', 'name')
    ordering = ('document_type', 'language', '-version')


@admin.register(GeneratedDocument)
class GeneratedDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'company',
        'tender_lot',
        'document_type',
        'language',
        'status',
        'edit_version',
        'updated_at',
    )
    list_filter = ('status', 'document_type', 'language')
    search_fields = (
        'title',
        'company__company_name',
        'company__stir',
        'tender_lot__lot_number',
    )
    readonly_fields = (
        'content_html',
        'content_text',
        'context_snapshot',
        'generation_metadata',
        'created_at',
        'updated_at',
    )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(GeneratedDocumentRevision)
class GeneratedDocumentRevisionAdmin(admin.ModelAdmin):
    list_display = ('document', 'version', 'source', 'created_by', 'created_at')
    list_filter = ('source',)
    search_fields = ('document__title',)
    readonly_fields = (
        'document',
        'version',
        'title',
        'content_json',
        'content_html',
        'content_text',
        'source',
        'change_summary',
        'created_by',
        'created_at',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(DocumentExport)
class DocumentExportAdmin(admin.ModelAdmin):
    list_display = (
        'document',
        'format',
        'status',
        'requested_by',
        'file_size',
        'created_at',
    )
    list_filter = ('format', 'status')
    search_fields = ('document__title', 'checksum_sha256')
    readonly_fields = (
        'document',
        'revision',
        'requested_by',
        'format',
        'status',
        'file',
        'storage_key',
        'checksum_sha256',
        'file_size',
        'metadata',
        'error_message',
        'started_at',
        'completed_at',
        'failed_at',
        'created_at',
        'updated_at',
    )


@admin.register(DocumentAuditEvent)
class DocumentAuditEventAdmin(admin.ModelAdmin):
    list_display = ('document', 'event', 'actor', 'created_at')
    list_filter = ('event',)
    search_fields = ('document__title',)
    readonly_fields = ('document', 'actor', 'event', 'metadata', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
