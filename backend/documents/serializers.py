from django.urls import reverse
from rest_framework import serializers

from documents.models import (
    DocumentExport,
    GeneratedDocument,
    GeneratedDocumentRevision,
    TenderDocumentTemplate,
)
from documents.services.exports import create_download_token


class TenderDocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenderDocumentTemplate
        fields = [
            'id',
            'code',
            'name',
            'document_type',
            'language',
            'version',
            'content_schema',
            'required_company_fields',
        ]
        read_only_fields = fields


class GenerateDocumentSerializer(serializers.Serializer):
    company_id = serializers.UUIDField(required=False)
    tender_lot_id = serializers.UUIDField()
    template_id = serializers.UUIDField()
    analysis_id = serializers.UUIDField(required=False, allow_null=True)
    title = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        default='',
    )
    user_instructions = serializers.CharField(
        max_length=4000,
        required=False,
        allow_blank=True,
        default='',
    )


class UpdateDocumentSerializer(serializers.Serializer):
    edit_version = serializers.IntegerField(min_value=1)
    title = serializers.CharField(max_length=500, required=False)
    content_json = serializers.JSONField()
    change_summary = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        default='',
    )


class ApproveDocumentSerializer(serializers.Serializer):
    edit_version = serializers.IntegerField(min_value=1)


class ExportDocumentSerializer(serializers.Serializer):
    format = serializers.ChoiceField(choices=DocumentExport.Format.choices)


class GeneratedDocumentRevisionSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = GeneratedDocumentRevision
        fields = [
            'id',
            'version',
            'title',
            'content_json',
            'content_html',
            'content_text',
            'source',
            'change_summary',
            'created_by',
            'created_at',
        ]
        read_only_fields = fields

    def get_created_by(self, obj):
        if obj.created_by is None:
            return None
        return {
            'id': obj.created_by_id,
            'name': obj.created_by.display_name,
        }


class DocumentExportSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = DocumentExport
        fields = [
            'id',
            'document_id',
            'revision_id',
            'format',
            'status',
            'checksum_sha256',
            'file_size',
            'metadata',
            'error_message',
            'download_url',
            'started_at',
            'completed_at',
            'failed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_download_url(self, obj):
        if obj.status != DocumentExport.Status.COMPLETED or not obj.file:
            return None
        request = self.context.get('request')
        path = reverse('api-v1:documents:export-download', args=[obj.id])
        url = f'{path}?token={create_download_token(obj)}'
        return request.build_absolute_uri(url) if request else url


class GeneratedDocumentListSerializer(serializers.ModelSerializer):
    template = TenderDocumentTemplateSerializer(read_only=True)
    author = serializers.SerializerMethodField()

    class Meta:
        model = GeneratedDocument
        fields = [
            'id',
            'title',
            'document_type',
            'language',
            'status',
            'template',
            'tender_lot_id',
            'author',
            'edit_version',
            'error_message',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_author(self, obj):
        return {
            'id': obj.created_by_id,
            'name': obj.created_by.display_name,
        }


class GeneratedDocumentDetailSerializer(GeneratedDocumentListSerializer):
    exports = DocumentExportSerializer(many=True, read_only=True)

    class Meta(GeneratedDocumentListSerializer.Meta):
        fields = GeneratedDocumentListSerializer.Meta.fields + [
            'company_id',
            'analysis_id',
            'content_json',
            'content_html',
            'content_text',
            'context_snapshot',
            'generation_metadata',
            'template_version',
            'generated_at',
            'approved_at',
            'exported_at',
            'failed_at',
            'archived_at',
            'exports',
        ]
