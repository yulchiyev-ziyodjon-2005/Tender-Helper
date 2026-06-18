import tempfile
from datetime import timedelta
from unittest.mock import patch
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from companies.models import CompanyProfile
from documents.models import (
    DocumentAuditEvent,
    DocumentExport,
    GeneratedDocument,
    GeneratedDocumentRevision,
    TenderDocumentTemplate,
)
from documents.services.providers import (
    DocumentGenerationProvider,
    DocumentGenerationResult,
    DocumentProviderUnavailable,
)
from subscriptions.models import SubscriptionPlan, UsageRecord
from subscriptions.services.billing import activate_subscription
from tenders.models import TenderLot, TenderSource
from users.models import CustomUser


def canonical_content(text='Xavfsiz hujjat matni'):
    return {
        'type': 'document',
        'version': 1,
        'content': [
            {
                'type': 'heading',
                'attrs': {'level': 2},
                'content': [{'type': 'text', 'text': 'Rasmiy hujjat'}],
            },
            {
                'type': 'paragraph',
                'content': [{'type': 'text', 'text': text}],
            },
        ],
    }


class SuccessfulDocumentProvider(DocumentGenerationProvider):
    provider_code = 'test'

    def generate(self, *, template, context, user_instructions):
        return DocumentGenerationResult(
            content_json=canonical_content(
                '<script>alert(1)</script> Tasdiqlangan matn'
            ),
            metadata={
                'provider': self.provider_code,
                'model': 'test-model',
                'prompt_version': template.version,
                'schema_version': 1,
            },
        )


class FailingDocumentProvider(DocumentGenerationProvider):
    provider_code = 'test_failure'

    def generate(self, *, template, context, user_instructions):
        raise DocumentProviderUnavailable()


class InvalidDocumentProvider(DocumentGenerationProvider):
    provider_code = 'test_invalid'

    def generate(self, *, template, context, user_instructions):
        return DocumentGenerationResult(
            content_json={
                'type': 'document',
                'version': 1,
                'content': [{'type': 'script', 'content': []}],
            },
            metadata={'provider': self.provider_code},
        )


SUCCESS_PROVIDER = 'documents.tests.SuccessfulDocumentProvider'
FAIL_PROVIDER = 'documents.tests.FailingDocumentProvider'
INVALID_PROVIDER = 'documents.tests.InvalidDocumentProvider'


@override_settings(
    DOCUMENT_GENERATION_PROVIDER=SUCCESS_PROVIDER,
    CELERY_TASK_ALWAYS_EAGER=True,
)
class DocumentApiTests(APITestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.media_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)
        self.addCleanup(self.media_dir.cleanup)

        self.user = CustomUser.objects.create_user(
            phone_number='+998901113301',
            full_name='Document Owner',
        )
        self.client.force_authenticate(self.user)
        self.company = CompanyProfile.objects.create(
            user=self.user,
            stir='309333301',
            company_name='Document Test MChJ',
            company_type=CompanyProfile.CompanyType.MCHJ,
            industry='IT',
            director_name='Alisher Karimov',
            legal_address='Toshkent shahri',
            raw_tax_data={'secret_registry_field': 'must-not-leak'},
        )
        self.tender = TenderLot.objects.create(
            source=TenderSource.objects.get(
                code=TenderLot.PlatformSource.MANUAL,
            ),
            external_id='',
            lot_number='DOC-TEST-001',
            platform_source=TenderLot.PlatformSource.MANUAL,
            title='Server yetkazib berish',
            buyer_name='Test Buyurtmachi',
            start_price=100000000,
            region='Toshkent',
            category='IT',
            posted_date=timezone.now(),
            deadline=timezone.now() + timedelta(days=7),
        )
        self.template = TenderDocumentTemplate.objects.get(
            code='tender-application',
            language='uz',
            version=1,
        )
        self.activate_plan('business')

    def activate_plan(self, code):
        now = timezone.now()
        return activate_subscription(
            self.company,
            SubscriptionPlan.objects.get(code=code),
            period_start=now,
            period_end=now + timedelta(days=30),
        )

    def generate(self, **overrides):
        payload = {
            'company_id': self.company.id,
            'tender_lot_id': self.tender.id,
            'template_id': self.template.id,
            'user_instructions': 'Faktlardan tashqariga chiqmang.',
        }
        payload.update(overrides)
        return self.client.post(
            '/api/v1/documents/generate/',
            payload,
            format='json',
        )

    def test_templates_require_business_entitlement_and_hide_prompt(self):
        response = self.client.get('/api/v1/documents/templates/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)
        self.assertNotIn('prompt_template', response.data[0])

        self.activate_plan('free')
        denied = self.client.get('/api/v1/documents/templates/')
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(denied.data['code'], 'feature_not_available')

    def test_generation_requires_stir_and_required_template_fields(self):
        self.company.stir = None
        self.company.stir_skipped = True
        self.company.save(update_fields=['stir', 'stir_skipped', 'updated_at'])
        denied = self.generate()
        self.assertEqual(denied.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(denied.data['code'], 'stir_required')

        self.company.stir = '309333301'
        self.company.stir_skipped = False
        self.company.director_name = ''
        self.company.save(
            update_fields=[
                'stir',
                'stir_skipped',
                'director_name',
                'updated_at',
            ],
        )
        missing = self.generate()
        self.assertEqual(missing.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            missing.data['code'],
            'template_required_fields_missing',
        )
        self.assertEqual(missing.data['details']['fields'], ['director_name'])

    def test_generation_creates_sanitized_draft_revision_usage_and_audit(self):
        response = self.generate()

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], GeneratedDocument.Status.DRAFT)
        self.assertEqual(response.data['edit_version'], 1)
        self.assertNotIn('<script>', response.data['content_html'])
        self.assertIn('&lt;script&gt;', response.data['content_html'])
        self.assertNotIn(
            'secret_registry_field',
            str(response.data['context_snapshot']),
        )
        document = GeneratedDocument.objects.get(pk=response.data['id'])
        self.assertEqual(document.revisions.count(), 1)
        self.assertEqual(
            document.revisions.get().source,
            GeneratedDocumentRevision.Source.GENERATION,
        )
        self.assertTrue(
            document.audit_events.filter(
                event=DocumentAuditEvent.Event.GENERATION_COMPLETED,
            ).exists(),
        )
        usage = UsageRecord.objects.get(
            company=self.company,
            metric=UsageRecord.Metric.DOCUMENT_GENERATION,
        )
        self.assertEqual(usage.used, 1)

    @override_settings(DOCUMENT_GENERATION_PROVIDER=FAIL_PROVIDER)
    def test_provider_failure_is_real_failed_state_without_fake_draft(self):
        response = self.generate()

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], GeneratedDocument.Status.FAILED)
        self.assertEqual(response.data['content_json'], {})
        self.assertEqual(response.data['content_html'], '')
        self.assertEqual(
            GeneratedDocumentRevision.objects.filter(
                document_id=response.data['id'],
            ).count(),
            0,
        )

    @override_settings(DOCUMENT_GENERATION_PROVIDER=INVALID_PROVIDER)
    def test_invalid_provider_output_is_failed_not_persisted(self):
        response = self.generate()

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], GeneratedDocument.Status.FAILED)
        self.assertEqual(response.data['content_json'], {})
        self.assertNotIn('<script>', response.data['content_html'])

    def test_edit_sanitizes_content_and_rejects_stale_version(self):
        generated = self.generate()
        document_id = generated.data['id']
        payload = {
            'edit_version': 1,
            'content_json': canonical_content(
                '<img src=x onerror=alert(1)> Yangi matn'
            ),
            'change_summary': 'User edit',
        }

        first = self.client.patch(
            f'/api/v1/documents/{document_id}/',
            payload,
            format='json',
        )
        stale = self.client.patch(
            f'/api/v1/documents/{document_id}/',
            payload,
            format='json',
        )

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(first.data['edit_version'], 2)
        self.assertNotIn('<img', first.data['content_html'])
        self.assertEqual(stale.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(stale.data['code'], 'edit_version_conflict')
        self.assertEqual(stale.data['details']['current_edit_version'], 2)

    def test_invalid_canonical_content_is_rejected(self):
        generated = self.generate()
        response = self.client.patch(
            f"/api/v1/documents/{generated.data['id']}/",
            {
                'edit_version': 1,
                'content_json': {
                    'type': 'document',
                    'version': 1,
                    'content': [{
                        'type': 'iframe',
                        'attrs': {'src': 'javascript:alert(1)'},
                    }],
                },
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'invalid_document_content')

    def test_export_requires_explicit_approval(self):
        generated = self.generate()
        response = self.client.post(
            f"/api/v1/documents/{generated.data['id']}/export/",
            {'format': DocumentExport.Format.PDF},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['code'], 'document_state_conflict')
        self.assertFalse(DocumentExport.objects.exists())

    def test_approval_versions_and_pdf_export_with_signed_download(self):
        generated = self.generate()
        document_id = generated.data['id']
        approved = self.client.post(
            f'/api/v1/documents/{document_id}/approve/',
            {'edit_version': 1},
            format='json',
        )
        exported = self.client.post(
            f'/api/v1/documents/{document_id}/export/',
            {'format': DocumentExport.Format.PDF},
            format='json',
        )

        self.assertEqual(approved.status_code, status.HTTP_200_OK)
        self.assertEqual(approved.data['status'], GeneratedDocument.Status.APPROVED)
        self.assertEqual(exported.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(exported.data['status'], DocumentExport.Status.COMPLETED)
        self.assertEqual(len(exported.data['checksum_sha256']), 64)
        self.assertGreater(exported.data['file_size'], 0)
        self.assertIsNotNone(exported.data['download_url'])

        invalid = self.client.get(
            f"/api/v1/documents/exports/{exported.data['id']}/download/"
            '?token=invalid',
        )
        self.assertEqual(invalid.status_code, status.HTTP_403_FORBIDDEN)

        download_path = urlsplit(exported.data['download_url']).path
        download_query = urlsplit(exported.data['download_url']).query
        valid = self.client.get(f'{download_path}?{download_query}')
        self.assertEqual(valid.status_code, status.HTTP_200_OK)
        for closer in valid._resource_closers:
            closer()
        valid._resource_closers.clear()
        self.assertEqual(
            GeneratedDocumentRevision.objects.filter(
                document_id=document_id,
            ).count(),
            2,
        )
        self.assertEqual(
            UsageRecord.objects.get(
                company=self.company,
                metric=UsageRecord.Metric.DOCUMENT_EXPORT,
            ).used,
            1,
        )

    def test_docx_export_is_valid_zip_payload(self):
        generated = self.generate()
        document_id = generated.data['id']
        self.client.post(
            f'/api/v1/documents/{document_id}/approve/',
            {'edit_version': 1},
            format='json',
        )
        response = self.client.post(
            f'/api/v1/documents/{document_id}/export/',
            {'format': DocumentExport.Format.DOCX},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        export = DocumentExport.objects.get(pk=response.data['id'])
        with export.file.open('rb') as exported_file:
            self.assertEqual(exported_file.read(2), b'PK')

    @patch(
        'documents.services.exports._build_pdf',
        side_effect=RuntimeError('renderer unavailable'),
    )
    def test_export_failure_is_recorded_without_losing_approval(self, renderer):
        generated = self.generate()
        document_id = generated.data['id']
        self.client.post(
            f'/api/v1/documents/{document_id}/approve/',
            {'edit_version': 1},
            format='json',
        )

        response = self.client.post(
            f'/api/v1/documents/{document_id}/export/',
            {'format': DocumentExport.Format.PDF},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['status'], DocumentExport.Status.FAILED)
        document = GeneratedDocument.objects.get(pk=document_id)
        self.assertEqual(document.status, GeneratedDocument.Status.APPROVED)
        self.assertTrue(
            document.audit_events.filter(
                event=DocumentAuditEvent.Event.EXPORT_FAILED,
            ).exists(),
        )

    def test_other_user_cannot_read_edit_or_download_document(self):
        generated = self.generate()
        other = CustomUser.objects.create_user(
            phone_number='+998901113302',
        )
        self.client.force_authenticate(other)

        detail = self.client.get(
            f"/api/v1/documents/{generated.data['id']}/",
        )
        edit = self.client.patch(
            f"/api/v1/documents/{generated.data['id']}/",
            {
                'edit_version': 1,
                'content_json': canonical_content(),
            },
            format='json',
        )

        self.assertEqual(detail.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(edit.status_code, status.HTTP_404_NOT_FOUND)

    def test_document_list_filters_and_versions_endpoint(self):
        generated = self.generate()
        listed = self.client.get(
            '/api/v1/documents/?status=draft&language=uz'
        )
        versions = self.client.get(
            f"/api/v1/documents/{generated.data['id']}/versions/",
        )

        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual(listed.data['count'], 1)
        self.assertEqual(len(listed.data['results']), 1)
        self.assertEqual(versions.status_code, status.HTTP_200_OK)
        self.assertEqual(versions.data[0]['version'], 1)

    def test_template_versions_are_immutable(self):
        self.template.prompt_template = 'Changed in place'

        with self.assertRaises(ValidationError):
            self.template.save()

    def test_database_rejects_zero_generated_template_version(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            GeneratedDocument.objects.create(
                company=self.company,
                tender_lot=self.tender,
                template=self.template,
                created_by=self.user,
                title='Invalid template version',
                document_type=self.template.document_type,
                language=self.template.language,
                template_version=0,
            )

    def test_document_endpoints_require_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get('/api/v1/documents/')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
