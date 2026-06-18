import csv
import io
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Count, Max, Prefetch, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from analysis.models import AITenderAnalysis
from companies.models import CompanyProfile
from competitors.models import (
    CompetitorAnalytics,
    CompetitorDataQualityIssue,
)
from core.pagination import StandardPageNumberPagination
from controlplane.constants import AdminCapability
from controlplane.exceptions import AdminAccessDenied, AdminConflict
from controlplane.models import (
    AdminAuditEvent,
    AdminPrincipal,
    FeatureFlag,
    SystemSetting,
)
from controlplane.permissions import (
    AdminCapabilityPermission,
    get_admin_principal,
)
from controlplane.serializers import (
    AdminStepUpSerializer,
    CapabilityAssignmentSerializer,
    FeatureFlagActionSerializer,
    MaintenanceBannerActionSerializer,
    PIIRevealSerializer,
    PlanPreviewSerializer,
    PlanUpdateSerializer,
    SubscriptionActionSerializer,
    SubscriptionActionPreviewSerializer,
    TemplatePublishActionSerializer,
    UserStatusActionSerializer,
)
from controlplane.services.actions import (
    MutationOutcome,
    execute_admin_action,
)
from controlplane.services.mfa import get_admin_mfa_provider
from documents.models import GeneratedDocument, TenderDocumentTemplate
from subscriptions.constants import FEATURE_POLICIES, CompanyRole, Feature
from subscriptions.models import (
    CompanySubscription,
    PaymentTransaction,
    SubscriptionPlan,
    UsageRecord,
    WebhookEvent,
)
from subscriptions.services.billing import (
    activate_subscription,
    cancel_subscription,
    extend_subscription,
    pause_subscription,
    peek_effective_subscription,
    schedule_plan_change,
)
from controlplane.services.flags import feature_is_enabled
from users.models import CustomUser


def _mask_email(value):
    if not value or '@' not in value:
        return None
    local, domain = value.split('@', 1)
    return f'{local[:1]}***@{domain}'


def _mask_phone(value):
    if not value:
        return None
    return f'***{value[-4:]}'


def _mask_stir(value):
    if not value:
        return None
    return f'*****{value[-4:]}'


def _csv_safe(value):
    text = '' if value is None else str(value)
    if text.startswith(('=', '+', '-', '@')):
        return f"'{text}"
    return text


def _version(value):
    return value.isoformat() if value else 'none'


def _action_response(result):
    data = dict(result.data)
    data['idempotent_replay'] = result.replayed
    succeeded = result.status_code < 400
    data['notification'] = {
        'status': 'success' if succeeded else 'error',
        'message': (
            (
                'Privileged action replayed safely.'
                if result.replayed
                else 'Privileged action completed.'
            )
            if succeeded
            else 'Privileged action failed previously; no mutation replayed.'
        ),
    }
    return Response(data, status=result.status_code)


def _serialize_plan(plan):
    return {
        'id': plan.id,
        'code': plan.code,
        'name': plan.name,
        'features': plan.features,
        'limits': plan.limits,
        'price_uzs': plan.price_uzs,
        'currency': plan.currency,
        'billing_period': plan.billing_period,
        'is_active': plan.is_active,
        'is_public': plan.is_public,
        'version': _version(plan.updated_at),
    }


def _serialize_subscription(subscription):
    return {
        'id': subscription.id,
        'company_id': subscription.company_id,
        'plan': subscription.plan.code,
        'status': subscription.status,
        'period_start': subscription.current_period_start,
        'period_end': subscription.current_period_end,
        'cancel_at_period_end': subscription.cancel_at_period_end,
        'scheduled_plan': (
            subscription.scheduled_plan.code
            if subscription.scheduled_plan_id
            else None
        ),
        'scheduled_change_at': subscription.scheduled_change_at,
        'scheduled_period_end': subscription.scheduled_period_end,
        'version': _version(subscription.updated_at),
    }


def _metric_range(request):
    now = timezone.now()
    range_key = request.query_params.get('range', '30d')
    durations = {
        '7d': timedelta(days=7),
        '30d': timedelta(days=30),
        '90d': timedelta(days=90),
    }
    if range_key == 'today':
        local_now = timezone.localtime(now)
        start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif range_key in durations:
        start = now - durations[range_key]
    elif range_key == 'custom':
        start = parse_datetime(request.query_params.get('start', ''))
        end = parse_datetime(request.query_params.get('end', ''))
        if (
            start is None
            or end is None
            or timezone.is_naive(start)
            or timezone.is_naive(end)
            or end <= start
            or end > now
        ):
            raise ValidationError({
                'range': (
                    'Custom range requires valid start/end values, with '
                    'start < end <= now.'
                ),
            })
        return range_key, start, end
    else:
        raise ValidationError({
            'range': 'Use today, 7d, 30d, 90d, or custom.',
        })
    return range_key, start, now


def _entitlement_preview(company, plan):
    rows = []
    for feature in Feature.ALL:
        policy = FEATURE_POLICIES[feature]
        enabled, disabled_reason = feature_is_enabled(feature)
        denial_code = None
        if feature not in plan.features:
            denial_code = 'feature_not_available'
        elif not enabled:
            denial_code = 'feature_temporarily_disabled'
        elif policy.requires_stir and not company.has_stir_identity:
            denial_code = 'stir_required'
        rows.append({
            'feature': feature,
            'allowed': denial_code is None,
            'denial_code': denial_code,
            'required_plan': policy.required_plan,
            'requires_stir': policy.requires_stir,
            'role': CompanyRole.OWNER,
            'kill_switch_enabled': enabled,
            'kill_switch_reason': disabled_reason,
        })
    return rows


class CapabilityMixin:
    permission_classes = [IsAuthenticated, AdminCapabilityPermission]


class CapabilityView(CapabilityMixin, APIView):
    pass


class AdminStepUpView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        principal = get_admin_principal(request.user)
        serializer = AdminStepUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password_ok = request.user.check_password(
            serializer.validated_data['password'],
        )
        mfa_ok = get_admin_mfa_provider().verify(
            user=request.user,
            code=serializer.validated_data['mfa_code'],
        )
        if not password_ok or not mfa_ok:
            AdminAuditEvent.objects.create(
                actor=request.user,
                capability='admin_auth',
                action='admin.step_up',
                target_type='admin_principal',
                target_id=str(principal.id),
                reason='Administrator step-up authentication',
                outcome=AdminAuditEvent.Outcome.FAILURE,
            )
            raise AdminAccessDenied(
                code='admin_step_up_failed',
                message='Password or MFA verification failed.',
            )
        now = timezone.now()
        principal.mfa_verified_at = now
        principal.step_up_at = now
        principal.save(update_fields=[
            'mfa_verified_at',
            'step_up_at',
            'updated_at',
        ])
        AdminAuditEvent.objects.create(
            actor=request.user,
            capability='admin_auth',
            action='admin.step_up',
            target_type='admin_principal',
            target_id=str(principal.id),
            reason='Administrator step-up authentication',
            outcome=AdminAuditEvent.Outcome.SUCCESS,
        )
        return Response({
            'status': 'verified',
            'mfa_verified_at': now,
            'step_up_at': now,
        })


class OverviewView(CapabilityView):
    required_capability = AdminCapability.OVERVIEW

    def get(self, request):
        range_key, start, now = _metric_range(request)
        user_total = CustomUser.objects.count()
        company_total = CompanyProfile.objects.count()
        usage = {
            row['metric']: row['used']
            for row in UsageRecord.objects.values('metric').annotate(
                used=Sum('used'),
            )
        }
        subscriptions = {
            row['status']: row['count']
            for row in CompanySubscription.objects.values('status').annotate(
                count=Count('id'),
            )
        }
        plans = {
            row['plan__code']: row['count']
            for row in CompanySubscription.objects.filter(
                status__in=CompanySubscription.EFFECTIVE_CANDIDATE_STATUSES,
            ).values('plan__code').annotate(count=Count('id'))
        }
        latest_competitor = CompetitorAnalytics.objects.aggregate(
            value=Max('calculated_at'),
        )['value']
        return Response({
            'environment': settings.APP_ENV,
            'range': {
                'key': range_key,
                'start': start,
                'end': now,
                'timezone': settings.TIME_ZONE,
            },
            'updated_at': now,
            'growth': {
                'source_status': 'live',
                'freshness_seconds': 300,
                'updated_at': now,
                'interval': range_key,
                'total_users': user_total,
                'new_users': CustomUser.objects.filter(
                    date_joined__gte=start,
                ).count(),
                'active_accounts': CustomUser.objects.filter(
                    is_active=True,
                ).count(),
                'companies': company_total,
                'stir_completion_rate': (
                    round(
                        CompanyProfile.objects.exclude(
                            stir__isnull=True,
                        ).count() / company_total * 100,
                        2,
                    )
                    if company_total
                    else 0
                ),
            },
            'subscriptions': {
                'source_status': 'live',
                'freshness_seconds': 300,
                'updated_at': now,
                'interval': range_key,
                'by_status': subscriptions,
                'by_plan': plans,
            },
            'business_usage': {
                'source_status': 'partial',
                'freshness_seconds': 300,
                'updated_at': now,
                'interval': 'billing_period_snapshots',
                'metrics': usage,
                'note': (
                    'UsageRecord stores billing-period aggregates, not '
                    'event timestamps.'
                ),
            },
            'ai': {
                'source_status': 'partial',
                'freshness_seconds': 60,
                'updated_at': now,
                'interval': range_key,
                'requests': AITenderAnalysis.objects.filter(
                    created_at__gte=start,
                ).count(),
                'failures': AITenderAnalysis.objects.filter(
                    created_at__gte=start,
                    analysis_status=AITenderAnalysis.Status.FAILED,
                ).count(),
                'tokens': None,
                'cost': None,
                'latency': None,
            },
            'operations': {
                'source_status': 'partial',
                'freshness_seconds': 60,
                'updated_at': now,
                'failed_documents': GeneratedDocument.objects.filter(
                    status=GeneratedDocument.Status.FAILED,
                ).count(),
                'competitor_calculated_at': latest_competitor,
                'competitor_quality_issues': (
                    CompetitorDataQualityIssue.objects.filter(
                        resolved_at__isnull=True,
                    ).count()
                ),
                'queue': {'source_status': 'unavailable'},
                'scraping': {'source_status': 'unavailable'},
                'payments': {'source_status': 'unavailable'},
            },
            'revenue': {
                'source_status': 'unavailable',
                'updated_at': now,
                'interval': range_key,
                'mrr': None,
                'paid_amount': None,
                'failed_payments': None,
                'refunds': None,
            },
        })


class AdminUserListView(CapabilityMixin, generics.ListAPIView):
    required_capability = AdminCapability.SUPPORT

    def get_queryset(self):
        queryset = CustomUser.objects.prefetch_related('company_profiles')
        query = self.request.query_params.get('search', '').strip()
        if query:
            queryset = queryset.filter(
                Q(full_name__icontains=query)
                | Q(email__icontains=query)
                | Q(phone_number__icontains=query)
                | Q(company_profiles__company_name__icontains=query)
                | Q(company_profiles__stir__icontains=query)
            ).distinct()
        return queryset.order_by('-date_joined')

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        rows = page if page is not None else self.get_queryset()
        data = [{
            'id': user.id,
            'full_name': user.full_name,
            'email': _mask_email(user.email),
            'phone_number': _mask_phone(user.phone_number),
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'last_login': user.last_login,
            'date_joined': user.date_joined,
            'companies': [
                {
                    'id': company.id,
                    'name': company.company_name,
                    'stir': _mask_stir(company.stir),
                    'plan': company.current_tariff,
                }
                for company in user.company_profiles.all()
            ],
            'version': str(user.auth_version),
        } for user in rows]
        if page is not None:
            return self.get_paginated_response(data)
        return Response(data)


class AdminGlobalSearchView(CapabilityView):
    required_capability = AdminCapability.SUPPORT

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if len(query) < 2:
            raise ValidationError({'q': 'Enter at least 2 characters.'})
        users = CustomUser.objects.filter(
            Q(full_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone_number__icontains=query)
        ).order_by('-date_joined')[:10]
        companies = CompanyProfile.objects.filter(
            Q(company_name__icontains=query)
            | Q(stir__icontains=query)
        ).order_by('-created_at')[:10]
        return Response({
            'query': query,
            'users': [{
                'id': user.id,
                'name': user.display_name,
                'email': _mask_email(user.email),
                'phone_number': _mask_phone(user.phone_number),
                'is_active': user.is_active,
            } for user in users],
            'companies': [{
                'id': company.id,
                'name': company.company_name,
                'stir': _mask_stir(company.stir),
                'registry_status': company.registry_status,
                'plan': company.current_tariff,
            } for company in companies],
        })


class AdminUserDetailView(CapabilityView):
    required_capability = AdminCapability.SUPPORT

    def get(self, request, user_id):
        user = get_object_or_404(
            CustomUser.objects.prefetch_related(
                'company_profiles__subscriptions__plan',
                'company_profiles__subscriptions__scheduled_plan',
                'company_profiles__usage_records',
                'company_registry_drafts',
            ),
            pk=user_id,
        )
        timeline = [{
            'type': 'account_created',
            'at': user.date_joined,
            'status': 'completed',
        }]
        if user.last_login:
            timeline.append({
                'type': 'last_login',
                'at': user.last_login,
                'status': 'completed',
            })
        for draft in user.company_registry_drafts.all()[:20]:
            timeline.append({
                'type': 'registry_lookup',
                'at': draft.created_at,
                'status': draft.status,
                'company_id': draft.profile_id,
                'reference': str(draft.id),
            })
        for company in user.company_profiles.all():
            for subscription in company.subscriptions.all()[:20]:
                timeline.append({
                    'type': 'subscription',
                    'at': subscription.created_at,
                    'status': subscription.status,
                    'company_id': company.id,
                    'reference': str(subscription.id),
                    'plan': subscription.plan.code,
                })
        timeline.sort(key=lambda item: item['at'], reverse=True)
        return Response({
            'id': user.id,
            'full_name': user.full_name,
            'email': _mask_email(user.email),
            'phone_number': _mask_phone(user.phone_number),
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'auth_provider': user.auth_provider,
            'auth_version': user.auth_version,
            'last_login': user.last_login,
            'date_joined': user.date_joined,
            'companies': [{
                'id': company.id,
                'name': company.company_name,
                'stir': _mask_stir(company.stir),
                'registry_status': company.registry_status,
                'plan': company.current_tariff,
                'usage': [{
                    'metric': usage.metric,
                    'used': usage.used,
                    'limit_snapshot': usage.limit_snapshot,
                    'period_end': usage.period_end,
                } for usage in company.usage_records.all()[:20]],
            } for company in user.company_profiles.all()],
            'timeline': timeline[:100],
            'version': str(user.auth_version),
        })


class AdminCompanyListView(CapabilityMixin, generics.ListAPIView):
    required_capability = AdminCapability.SUPPORT

    def get_queryset(self):
        queryset = CompanyProfile.objects.select_related(
            'user',
        ).prefetch_related(
            Prefetch(
                'usage_records',
                queryset=UsageRecord.objects.order_by('-period_end'),
                to_attr='admin_usage_records',
            ),
        ).annotate(
            generated_document_count=Count(
                'generated_documents',
                distinct=True,
            ),
            analysis_count=Count('analyses', distinct=True),
        )
        query = self.request.query_params.get('search', '').strip()
        if query:
            queryset = queryset.filter(
                Q(company_name__icontains=query)
                | Q(stir__icontains=query)
                | Q(user__full_name__icontains=query)
                | Q(user__email__icontains=query)
                | Q(user__phone_number__icontains=query)
            )
        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        rows = page if page is not None else self.get_queryset()
        data = [{
            'id': company.id,
            'company_name': company.company_name,
            'stir': _mask_stir(company.stir),
            'registry_status': company.registry_status,
            'owner': {
                'id': company.user_id,
                'name': company.user.full_name,
                'email': _mask_email(company.user.email),
                'phone_number': _mask_phone(company.user.phone_number),
            },
            'plan': company.current_tariff,
            'usage': [
                {
                    'metric': item.metric,
                    'used': item.used,
                    'limit_snapshot': item.limit_snapshot,
                    'period_end': item.period_end,
                }
                for item in company.admin_usage_records[:20]
            ],
            'generated_documents': company.generated_document_count,
            'analyses': company.analysis_count,
            'created_at': company.created_at,
        } for company in rows]
        if page is not None:
            return self.get_paginated_response(data)
        return Response(data)


class AdminCompanyDetailView(CapabilityView):
    required_capability = AdminCapability.SUPPORT

    def get(self, request, company_id):
        company = get_object_or_404(
            CompanyProfile.objects.select_related('user').prefetch_related(
                'subscriptions__plan',
                'subscriptions__scheduled_plan',
                'usage_records',
                'generated_documents',
                'analyses',
            ),
            pk=company_id,
        )
        effective = peek_effective_subscription(company)
        effective_plan = (
            effective.plan
            if effective
            else SubscriptionPlan.objects.get(code='free', is_active=True)
        )
        return Response({
            'id': company.id,
            'company_name': company.company_name,
            'stir': _mask_stir(company.stir),
            'registry_status': company.registry_status,
            'registry_source': company.registry_source,
            'registry_fetched_at': company.registry_fetched_at,
            'owner': {
                'id': company.user_id,
                'name': company.user.display_name,
                'email': _mask_email(company.user.email),
                'phone_number': _mask_phone(company.user.phone_number),
            },
            'membership': [{
                'user_id': company.user_id,
                'role': CompanyRole.OWNER,
            }],
            'subscription': (
                _serialize_subscription(effective.subscription)
                if effective
                else None
            ),
            'effective_plan': effective_plan.code,
            'subscription_history': [
                _serialize_subscription(item)
                for item in company.subscriptions.all()[:50]
            ],
            'entitlements': _entitlement_preview(company, effective_plan),
            'usage': [{
                'metric': item.metric,
                'used': item.used,
                'limit_snapshot': item.limit_snapshot,
                'period_start': item.period_start,
                'period_end': item.period_end,
            } for item in company.usage_records.all()[:50]],
            'aggregates': {
                'generated_documents': len(company.generated_documents.all()),
                'analyses': len(company.analyses.all()),
            },
            'created_at': company.created_at,
            'updated_at': company.updated_at,
        })


class CompanyEntitlementPreviewView(CapabilityView):
    required_capability = AdminCapability.BILLING

    def get(self, request, company_id):
        company = get_object_or_404(CompanyProfile, pk=company_id)
        plan_code = request.query_params.get('plan')
        if plan_code:
            plan = get_object_or_404(SubscriptionPlan, code=plan_code)
            source = 'proposed'
        else:
            effective = peek_effective_subscription(company)
            plan = (
                effective.plan
                if effective
                else SubscriptionPlan.objects.get(code='free', is_active=True)
            )
            source = 'effective' if effective else 'free_fallback_preview'
        return Response({
            'company_id': company.id,
            'plan': plan.code,
            'source': source,
            'has_stir': company.has_stir_identity,
            'features': _entitlement_preview(company, plan),
            'limits': plan.limits,
            'generated_at': timezone.now(),
        })


class PlanListView(CapabilityView):
    required_capability = AdminCapability.BILLING

    def get(self, request):
        plans = SubscriptionPlan.objects.annotate(
            subscriber_count_value=Count(
                'company_subscriptions',
                filter=Q(company_subscriptions__status__in=(
                    CompanySubscription.EFFECTIVE_CANDIDATE_STATUSES
                )),
                distinct=True,
            ),
        ).order_by('rank', 'code')
        return Response([
            {
                **_serialize_plan(plan),
                'subscriber_count': plan.subscriber_count_value,
            }
            for plan in plans
        ])


class PlanPreviewView(CapabilityView):
    required_capability = AdminCapability.BILLING

    def post(self, request, plan_code):
        serializer = PlanPreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = get_object_or_404(SubscriptionPlan, code=plan_code)
        before = _serialize_plan(plan)
        for field, value in serializer.validated_data.items():
            setattr(plan, field, value)
        try:
            plan.full_clean(validate_unique=False)
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict) from exc
        proposed = _serialize_plan(plan)
        changed_fields = [
            field
            for field in serializer.validated_data
            if before[field] != proposed[field]
        ]
        affected = CompanySubscription.objects.filter(
            plan_id=plan.id,
            status__in=CompanySubscription.EFFECTIVE_CANDIDATE_STATUSES,
        ).count()
        scheduled = CompanySubscription.objects.filter(
            scheduled_plan_id=plan.id,
            scheduled_change_at__isnull=False,
        ).count()
        return Response({
            'plan': plan.code,
            'before': before,
            'proposed': proposed,
            'changed_fields': changed_fields,
            'affected_active_subscriptions': affected,
            'affected_scheduled_changes': scheduled,
            'requires_step_up_to_publish': True,
            'confirmation_summary': (
                f'Publish {len(changed_fields)} field change(s) to '
                f'{affected} active subscriber(s).'
            ),
            'generated_at': timezone.now(),
        })


class PlanUpdateView(CapabilityView):
    required_capability = AdminCapability.BILLING
    requires_step_up = True

    def post(self, request, plan_code):
        serializer = PlanUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        editable_fields = (
            'features',
            'limits',
            'price_uzs',
            'is_active',
            'is_public',
        )
        changes = {
            field: data[field]
            for field in editable_fields
            if field in data
        }
        payload = {
            'target_type': 'subscription_plan',
            'target_id': plan_code,
            'changes': changes,
            'expected_version': data['expected_version'],
        }

        def mutate():
            plan = get_object_or_404(
                SubscriptionPlan.objects.select_for_update(),
                code=plan_code,
            )
            current_version = _version(plan.updated_at)
            if current_version != data['expected_version']:
                raise AdminConflict(
                    code='admin_version_conflict',
                    message='Plan changed since it was loaded.',
                    details={'current_version': current_version},
                )
            before = _serialize_plan(plan)
            scheduled_count = CompanySubscription.objects.filter(
                scheduled_plan=plan,
                scheduled_change_at__isnull=False,
            ).count()
            if changes.get('is_active') is False and scheduled_count:
                raise AdminConflict(
                    code='plan_has_scheduled_changes',
                    message=(
                        'Plan cannot be deactivated while scheduled changes '
                        'target it.'
                    ),
                    details={'scheduled_changes': scheduled_count},
                )
            for field, value in changes.items():
                setattr(plan, field, value)
            try:
                plan.full_clean()
            except DjangoValidationError as exc:
                raise AdminConflict(
                    code='invalid_plan_configuration',
                    message='Plan configuration is invalid.',
                    details=exc.message_dict,
                ) from exc
            plan.save(update_fields=[*changes, 'updated_at'])
            after = _serialize_plan(plan)
            return MutationOutcome(
                target_type='subscription_plan',
                target_id=str(plan.id),
                before=before,
                after=after,
                response_data=after,
                metadata={
                    'affected_active_subscriptions': (
                        CompanySubscription.objects.filter(
                            plan=plan,
                            status__in=(
                                CompanySubscription
                                .EFFECTIVE_CANDIDATE_STATUSES
                            ),
                        ).count()
                    ),
                },
            )

        return _action_response(execute_admin_action(
            request=request,
            capability=self.required_capability,
            action='plan.update',
            reason=data['reason'],
            idempotency_key=data['idempotency_key'],
            payload=payload,
            callback=mutate,
        ))


class SubscriptionListView(CapabilityView):
    required_capability = AdminCapability.BILLING
    pagination_class = StandardPageNumberPagination

    def get(self, request):
        subscriptions = CompanySubscription.objects.select_related(
            'company',
            'plan',
            'scheduled_plan',
        )
        status_value = request.query_params.get('status')
        plan_code = request.query_params.get('plan')
        query = request.query_params.get('search', '').strip()
        if status_value:
            subscriptions = subscriptions.filter(status=status_value)
        if plan_code:
            subscriptions = subscriptions.filter(plan__code=plan_code)
        if query:
            subscriptions = subscriptions.filter(
                Q(company__company_name__icontains=query)
                | Q(company__stir__icontains=query)
            )
        subscriptions = subscriptions.order_by('-created_at')
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(subscriptions, request, view=self)
        return paginator.get_paginated_response([{
            **_serialize_subscription(item),
            'company_name': item.company.company_name,
        } for item in page])


class SubscriptionActionPreviewView(CapabilityView):
    required_capability = AdminCapability.BILLING

    def post(self, request, company_id):
        serializer = SubscriptionActionPreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        company = get_object_or_404(CompanyProfile, pk=company_id)
        current = (
            CompanySubscription.objects.filter(company=company)
            .select_related('plan', 'scheduled_plan')
            .order_by('-created_at')
            .first()
        )
        current_version = _version(current.updated_at if current else None)
        if current_version != data['expected_version']:
            raise AdminConflict(
                code='admin_version_conflict',
                message='Subscription changed since it was loaded.',
                details={'current_version': current_version},
            )
        before = _serialize_subscription(current) if current else None
        action = data['action']
        now = timezone.now()
        proposed = dict(before or {})
        if action in {'activate', 'upgrade', 'downgrade'}:
            plan = get_object_or_404(
                SubscriptionPlan,
                code=data['plan_code'],
                is_active=True,
            )
            if action != 'activate' and current is None:
                raise ValidationError({
                    'action': f'{action} requires a current subscription.',
                })
            if action == 'upgrade' and plan.rank <= current.plan.rank:
                raise ValidationError({
                    'plan_code': 'Upgrade target must have a higher rank.',
                })
            if action == 'downgrade' and plan.rank >= current.plan.rank:
                raise ValidationError({
                    'plan_code': 'Downgrade target must have a lower rank.',
                })
            if action == 'downgrade':
                effective_at = (
                    data.get('effective_at') or current.current_period_end
                )
                if effective_at <= now:
                    raise ValidationError({
                        'effective_at': 'Scheduled time must be in the future.',
                    })
                if effective_at < current.current_period_end:
                    raise ValidationError({
                        'effective_at': (
                            'Downgrade cannot precede the current period end.'
                        ),
                    })
                proposed.update({
                    'scheduled_plan': plan.code,
                    'scheduled_change_at': effective_at,
                    'scheduled_period_end': data.get('period_end'),
                })
            elif action == 'upgrade' and data.get('effective_at'):
                if data['effective_at'] <= now:
                    raise ValidationError({
                        'effective_at': 'Scheduled time must be in the future.',
                    })
                proposed.update({
                    'scheduled_plan': plan.code,
                    'scheduled_change_at': data['effective_at'],
                    'scheduled_period_end': data.get('period_end'),
                })
            else:
                period_end = data.get('period_end') or now + timedelta(days=30)
                if period_end <= now:
                    raise ValidationError({
                        'period_end': 'Period end must be in the future.',
                    })
                proposed.update({
                    'plan': plan.code,
                    'status': CompanySubscription.Status.ACTIVE,
                    'period_start': now,
                    'period_end': period_end,
                    'scheduled_plan': None,
                    'scheduled_change_at': None,
                    'scheduled_period_end': None,
                })
        elif current is None:
            raise ValidationError({
                'action': f'{action} requires a current subscription.',
            })
        elif action == 'pause':
            if current.status not in {
                CompanySubscription.Status.TRIALING,
                CompanySubscription.Status.ACTIVE,
                CompanySubscription.Status.PAST_DUE,
            }:
                raise ValidationError({
                    'action': 'Only a live subscription can be paused.',
                })
            proposed['status'] = CompanySubscription.Status.PAUSED
        elif action == 'cancel':
            if current.status in {
                CompanySubscription.Status.CANCELED,
                CompanySubscription.Status.EXPIRED,
            }:
                raise ValidationError({
                    'action': 'Subscription is already inactive.',
                })
            proposed['status'] = CompanySubscription.Status.CANCELED
        else:
            if current.status == CompanySubscription.Status.CANCELED:
                raise ValidationError({
                    'action': 'Canceled subscription cannot be extended.',
                })
            if data['period_end'] <= current.current_period_end:
                raise ValidationError({
                    'period_end': (
                        'New period end must extend the current period.'
                    ),
                })
            proposed['period_end'] = data['period_end']
        return Response({
            'company_id': company.id,
            'action': action,
            'before': before,
            'proposed': proposed,
            'affected_subscriptions': 1,
            'requires_step_up_to_apply': True,
            'confirmation_summary': (
                f'Apply {action} to {company.company_name}.'
            ),
            'generated_at': now,
        })


class PaymentListView(CapabilityView):
    required_capability = AdminCapability.BILLING

    def get(self, request):
        transactions = list(
            PaymentTransaction.objects.select_related('company', 'plan')
            .order_by('-created_at')[:50]
            .values(
                'public_id',
                'merchant_trans_id',
                'provider',
                'status',
                'amount',
                'currency',
                'provider_transaction_id',
                'provider_payment_id',
                'created_at',
                'prepared_at',
                'paid_at',
                'canceled_at',
                'company__company_name',
                'company__stir',
                'plan__code',
            )
        )
        webhooks = list(
            WebhookEvent.objects.select_related('transaction')
            .order_by('-received_at')[:50]
            .values(
                'provider',
                'event_type',
                'provider_event_id',
                'action',
                'status',
                'error_code',
                'error_message',
                'received_at',
                'processed_at',
                'transaction__merchant_trans_id',
            )
        )
        pending_count = PaymentTransaction.objects.filter(
            status__in=[
                PaymentTransaction.Status.PENDING,
                PaymentTransaction.Status.PREPARED,
            ],
        ).count()
        failed_count = PaymentTransaction.objects.filter(
            status__in=[
                PaymentTransaction.Status.FAILED,
                PaymentTransaction.Status.CANCELED,
                PaymentTransaction.Status.EXPIRED,
            ],
        ).count()
        return Response({
            'source_status': 'available',
            'updated_at': timezone.now(),
            'transactions': transactions,
            'webhooks': webhooks,
            'reconciliation': {
                'pending_manual_review': pending_count,
                'failed_or_canceled': failed_count,
                'automated_job': 'not_implemented',
            },
        })


class OperationsView(CapabilityView):
    required_capability = AdminCapability.OPERATIONS

    def get(self, request):
        maintenance = SystemSetting.objects.get(
            key=SystemSetting.MAINTENANCE_BANNER,
        )
        return Response({
            'updated_at': timezone.now(),
            'feature_flags': list(FeatureFlag.objects.values(
                'feature',
                'is_enabled',
                'reason',
                'version',
                'updated_at',
            )),
            'templates': list(TenderDocumentTemplate.objects.values(
                'id',
                'code',
                'language',
                'version',
                'is_active',
                'is_published',
                'updated_at',
            )),
            'maintenance_banner': {
                'value': maintenance.value,
                'version': maintenance.version,
                'updated_at': maintenance.updated_at,
            },
            'ai': {
                'source_status': 'partial',
                'failed': AITenderAnalysis.objects.filter(
                    analysis_status=AITenderAnalysis.Status.FAILED,
                ).count(),
            },
            'queue': {'source_status': 'unavailable'},
            'scraping': {'source_status': 'unavailable'},
            'notification_templates': {'source_status': 'unavailable'},
        })


class MaintenanceBannerActionView(CapabilityView):
    required_capability = AdminCapability.ROOT
    requires_step_up = True

    def post(self, request):
        serializer = MaintenanceBannerActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        value = {
            'enabled': data['enabled'],
            'message': data['message'].strip(),
            'severity': data['severity'],
            'starts_at': (
                data['starts_at'].isoformat()
                if data.get('starts_at')
                else None
            ),
            'ends_at': (
                data['ends_at'].isoformat()
                if data.get('ends_at')
                else None
            ),
        }
        payload = {
            'target_type': 'system_setting',
            'target_id': SystemSetting.MAINTENANCE_BANNER,
            'value': value,
            'expected_version': data['expected_version'],
        }

        def mutate():
            setting = SystemSetting.objects.select_for_update().get(
                key=SystemSetting.MAINTENANCE_BANNER,
            )
            if str(setting.version) != data['expected_version']:
                raise AdminConflict(
                    code='admin_version_conflict',
                    message='System setting changed since it was loaded.',
                    details={'current_version': str(setting.version)},
                )
            before = {
                'value': setting.value,
                'version': setting.version,
            }
            setting.value = value
            setting.version += 1
            setting.updated_by = request.user
            setting.save()
            after = {
                'value': setting.value,
                'version': setting.version,
                'updated_at': setting.updated_at,
            }
            return MutationOutcome(
                target_type='system_setting',
                target_id=setting.key,
                before=before,
                after=after,
                response_data={'key': setting.key, **after},
            )

        return _action_response(execute_admin_action(
            request=request,
            capability=self.required_capability,
            action='system_setting.maintenance_banner.update',
            reason=data['reason'],
            idempotency_key=data['idempotency_key'],
            payload=payload,
            callback=mutate,
        ))


class AuditListView(CapabilityMixin, generics.ListAPIView):
    required_capability = AdminCapability.AUDIT

    def get_queryset(self):
        queryset = AdminAuditEvent.objects.select_related('actor')
        action = self.request.query_params.get('action')
        outcome = self.request.query_params.get('outcome')
        capability = self.request.query_params.get('capability')
        target_type = self.request.query_params.get('target_type')
        actor_id = self.request.query_params.get('actor_id')
        start = parse_datetime(self.request.query_params.get('start', ''))
        end = parse_datetime(self.request.query_params.get('end', ''))
        if action:
            queryset = queryset.filter(action=action)
        if outcome:
            queryset = queryset.filter(outcome=outcome)
        if capability:
            queryset = queryset.filter(capability=capability)
        if target_type:
            queryset = queryset.filter(target_type=target_type)
        if actor_id:
            queryset = queryset.filter(actor_id=actor_id)
        if start:
            queryset = queryset.filter(created_at__gte=start)
        if end:
            queryset = queryset.filter(created_at__lte=end)
        return queryset

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        rows = page if page is not None else self.get_queryset()
        data = [{
            'id': item.id,
            'created_at': item.created_at,
            'actor_id': item.actor_id,
            'actor': item.actor.display_name,
            'capability': item.capability,
            'action': item.action,
            'target_type': item.target_type,
            'target_id': item.target_id,
            'reason': item.reason,
            'before': item.before,
            'after': item.after,
            'outcome': item.outcome,
            'request_id': item.request_id,
            'ip_address': item.ip_address,
            'metadata': item.metadata,
        } for item in rows]
        if page is not None:
            return self.get_paginated_response(data)
        return Response(data)


class AuditExportView(CapabilityView):
    required_capability = AdminCapability.AUDIT
    requires_step_up = True

    def post(self, request):
        serializer = PIIRevealSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rows = AdminAuditEvent.objects.select_related('actor').order_by(
            '-created_at',
        )[:10000]
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'created_at',
            'actor_id',
            'actor',
            'capability',
            'action',
            'target_type',
            'target_id',
            'reason',
            'outcome',
            'request_id',
            'ip_address',
        ])
        exported = 0
        for item in rows:
            writer.writerow([
                _csv_safe(item.created_at.isoformat()),
                _csv_safe(item.actor_id),
                _csv_safe(item.actor.display_name),
                _csv_safe(item.capability),
                _csv_safe(item.action),
                _csv_safe(item.target_type),
                _csv_safe(item.target_id),
                _csv_safe(item.reason),
                _csv_safe(item.outcome),
                _csv_safe(item.request_id),
                _csv_safe(item.ip_address),
            ])
            exported += 1
        AdminAuditEvent.objects.create(
            actor=request.user,
            capability=self.required_capability,
            action='audit.export',
            target_type='admin_audit_event',
            target_id='',
            reason=serializer.validated_data['reason'],
            outcome=AdminAuditEvent.Outcome.SUCCESS,
            metadata={'exported_rows': exported, 'format': 'csv'},
        )
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename="admin-audit.csv"'
        )
        return response


class UserActionView(CapabilityView):
    required_capability = AdminCapability.SUPPORT
    requires_step_up = True

    def post(self, request, user_id):
        serializer = UserStatusActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        payload = {
            'target_type': 'user',
            'target_id': str(user_id),
            'action': data['action'],
            'expected_version': data['expected_version'],
        }

        def mutate():
            user = get_object_or_404(
                CustomUser.objects.select_for_update(),
                pk=user_id,
            )
            if str(user.auth_version) != data['expected_version']:
                raise AdminConflict(
                    code='admin_version_conflict',
                    message='User changed since it was loaded.',
                    details={'current_version': str(user.auth_version)},
                )
            before = {
                'is_active': user.is_active,
                'auth_version': user.auth_version,
            }
            if data['action'] == 'block':
                user.is_active = False
                user.auth_version += 1
            elif data['action'] == 'unblock':
                user.is_active = True
                user.auth_version += 1
            else:
                user.auth_version += 1
            user.save(update_fields=['is_active', 'auth_version', 'updated_at'])
            after = {
                'is_active': user.is_active,
                'auth_version': user.auth_version,
            }
            return MutationOutcome(
                target_type='user',
                target_id=str(user.id),
                before=before,
                after=after,
                response_data={
                    'id': user.id,
                    **after,
                    'version': str(user.auth_version),
                },
            )

        return _action_response(execute_admin_action(
            request=request,
            capability=self.required_capability,
            action=f'user.{data["action"]}',
            reason=data['reason'],
            idempotency_key=data['idempotency_key'],
            payload=payload,
            callback=mutate,
        ))


class UserRevealView(CapabilityView):
    required_capability = AdminCapability.SUPPORT
    requires_step_up = True

    def post(self, request, user_id):
        serializer = PIIRevealSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(CustomUser, pk=user_id)
        AdminAuditEvent.objects.create(
            actor=request.user,
            capability=self.required_capability,
            action='user.pii_reveal',
            target_type='user',
            target_id=str(user.id),
            reason=serializer.validated_data['reason'],
            outcome=AdminAuditEvent.Outcome.SUCCESS,
            metadata={'fields': ['email', 'phone_number']},
        )
        return Response({
            'id': user.id,
            'email': user.email,
            'phone_number': user.phone_number,
            'full_name': user.full_name,
        })


class UserPIIExportView(CapabilityView):
    required_capability = AdminCapability.SUPPORT
    requires_step_up = True

    def post(self, request, user_id):
        serializer = PIIRevealSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(CustomUser, pk=user_id)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'id',
            'full_name',
            'email',
            'phone_number',
            'is_active',
            'date_joined',
        ])
        writer.writerow([
            _csv_safe(user.id),
            _csv_safe(user.full_name),
            _csv_safe(user.email),
            _csv_safe(user.phone_number),
            _csv_safe(user.is_active),
            _csv_safe(user.date_joined.isoformat()),
        ])
        AdminAuditEvent.objects.create(
            actor=request.user,
            capability=self.required_capability,
            action='user.pii_export',
            target_type='user',
            target_id=str(user.id),
            reason=serializer.validated_data['reason'],
            outcome=AdminAuditEvent.Outcome.SUCCESS,
            metadata={'fields': ['email', 'phone_number'], 'format': 'csv'},
        )
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = (
            f'attachment; filename="user-{user.id}.csv"'
        )
        return response


class FeatureFlagActionView(CapabilityView):
    required_capability = AdminCapability.OPERATIONS
    requires_step_up = True

    def post(self, request, feature):
        if feature not in Feature.ALL:
            raise AdminAccessDenied(
                code='unknown_feature',
                message='Unknown feature key.',
            )
        serializer = FeatureFlagActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        payload = {
            'target_type': 'feature_flag',
            'target_id': feature,
            'is_enabled': data['is_enabled'],
            'expected_version': data['expected_version'],
        }

        def mutate():
            flag, _ = FeatureFlag.objects.select_for_update().get_or_create(
                feature=feature,
            )
            if str(flag.version) != data['expected_version']:
                raise AdminConflict(
                    code='admin_version_conflict',
                    message='Feature flag changed since it was loaded.',
                    details={'current_version': str(flag.version)},
                )
            before = {
                'is_enabled': flag.is_enabled,
                'reason': flag.reason,
                'version': flag.version,
            }
            flag.is_enabled = data['is_enabled']
            flag.reason = data['reason']
            flag.version += 1
            flag.updated_by = request.user
            flag.save()
            after = {
                'is_enabled': flag.is_enabled,
                'reason': flag.reason,
                'version': flag.version,
            }
            return MutationOutcome(
                target_type='feature_flag',
                target_id=feature,
                before=before,
                after=after,
                response_data={'feature': feature, **after},
            )

        return _action_response(execute_admin_action(
            request=request,
            capability=self.required_capability,
            action='feature_flag.update',
            reason=data['reason'],
            idempotency_key=data['idempotency_key'],
            payload=payload,
            callback=mutate,
        ))


class SubscriptionActionView(CapabilityView):
    required_capability = AdminCapability.BILLING
    requires_step_up = True

    def post(self, request, company_id):
        serializer = SubscriptionActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        payload = {
            'target_type': 'company_subscription',
            'target_id': str(company_id),
            'action': data['action'],
            'plan_code': data.get('plan_code'),
            'period_end': data.get('period_end'),
            'effective_at': data.get('effective_at'),
            'expected_version': data['expected_version'],
        }

        def mutate():
            company = get_object_or_404(CompanyProfile, pk=company_id)
            current = (
                CompanySubscription.objects.select_for_update(of=('self',))
                .filter(company=company)
                .select_related('plan', 'scheduled_plan')
                .order_by('-created_at')
                .first()
            )
            current_version = _version(current.updated_at if current else None)
            if current_version != data['expected_version']:
                raise AdminConflict(
                    code='admin_version_conflict',
                    message='Subscription changed since it was loaded.',
                    details={'current_version': current_version},
                )
            before = (
                {
                    'id': str(current.id),
                    'plan': current.plan.code,
                    'status': current.status,
                    'period_end': current.current_period_end.isoformat(),
                    'scheduled_plan': (
                        current.scheduled_plan.code
                        if current.scheduled_plan_id
                        else None
                    ),
                    'scheduled_change_at': (
                        current.scheduled_change_at.isoformat()
                        if current.scheduled_change_at
                        else None
                    ),
                }
                if current
                else {}
            )
            try:
                if data['action'] in {'activate', 'upgrade', 'downgrade'}:
                    plan = get_object_or_404(
                        SubscriptionPlan,
                        code=data['plan_code'],
                        is_active=True,
                    )
                    now = timezone.now()
                    effective_at = data.get('effective_at')
                    if effective_at and effective_at <= now:
                        raise ValueError(
                            'effective_at must be in the future.'
                        )
                    if data['action'] == 'activate':
                        updated = activate_subscription(
                            company,
                            plan,
                            period_start=now,
                            period_end=data.get('period_end') or (
                                now + timedelta(days=30)
                            ),
                            metadata={
                                'admin_reason': data['reason'],
                                'admin_actor_id': str(request.user.id),
                            },
                        )
                    elif current is None:
                        raise ValueError(
                            f'{data["action"]} requires a subscription.'
                        )
                    elif data['action'] == 'downgrade':
                        if plan.rank >= current.plan.rank:
                            raise ValueError(
                                'Downgrade target must have a lower rank.'
                            )
                        updated = schedule_plan_change(
                            current,
                            plan,
                            effective_at or current.current_period_end,
                            period_end=data.get('period_end'),
                            require_period_end=True,
                        )
                    elif plan.rank <= current.plan.rank:
                        raise ValueError(
                            'Upgrade target must have a higher rank.'
                        )
                    elif effective_at:
                        updated = schedule_plan_change(
                            current,
                            plan,
                            effective_at,
                            period_end=data.get('period_end'),
                        )
                    else:
                        updated = activate_subscription(
                            company,
                            plan,
                            period_start=now,
                            period_end=data.get('period_end') or (
                                now + timedelta(days=30)
                            ),
                            metadata={
                                'admin_reason': data['reason'],
                                'admin_actor_id': str(request.user.id),
                            },
                        )
                elif data['action'] == 'pause':
                    if current is None:
                        raise ValueError('No subscription to pause.')
                    updated = pause_subscription(current)
                elif data['action'] == 'cancel':
                    if current is None:
                        raise ValueError('No subscription to cancel.')
                    updated = cancel_subscription(current)
                else:
                    if current is None:
                        raise ValueError('No subscription to extend.')
                    updated = extend_subscription(
                        current,
                        data['period_end'],
                    )
            except (AttributeError, ValueError) as exc:
                raise AdminConflict(
                    code='invalid_subscription_transition',
                    message=str(exc),
                ) from exc
            updated.refresh_from_db()
            updated = CompanySubscription.objects.select_related(
                'plan',
                'scheduled_plan',
            ).get(pk=updated.pk)
            after = _serialize_subscription(updated)
            return MutationOutcome(
                target_type='company_subscription',
                target_id=str(updated.id),
                before=before,
                after=after,
                response_data=after,
            )

        return _action_response(execute_admin_action(
            request=request,
            capability=self.required_capability,
            action=f'subscription.{data["action"]}',
            reason=data['reason'],
            idempotency_key=data['idempotency_key'],
            payload=payload,
            callback=mutate,
        ))


class TemplatePublishActionView(CapabilityView):
    required_capability = AdminCapability.CONTENT
    requires_step_up = True

    def post(self, request, template_id):
        serializer = TemplatePublishActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        payload = {
            'target_type': 'document_template',
            'target_id': str(template_id),
            'publish': data['publish'],
            'expected_version': data['expected_version'],
        }

        def mutate():
            template = get_object_or_404(
                TenderDocumentTemplate.objects.select_for_update(),
                pk=template_id,
            )
            current_version = _version(template.updated_at)
            if current_version != data['expected_version']:
                raise AdminConflict(
                    code='admin_version_conflict',
                    message='Template changed since it was loaded.',
                    details={'current_version': current_version},
                )
            before = {
                'is_active': template.is_active,
                'is_published': template.is_published,
            }
            if data['publish']:
                other_active = TenderDocumentTemplate.objects.filter(
                    code=template.code,
                    language=template.language,
                    is_active=True,
                ).exclude(pk=template.pk)
                deactivated_ids = [
                    str(item)
                    for item in other_active.values_list('id', flat=True)
                ]
                other_active.update(
                    is_active=False,
                    updated_at=timezone.now(),
                )
                template.is_active = True
                template.is_published = True
            else:
                deactivated_ids = []
                template.is_active = False
                template.is_published = False
            template.save(update_fields=[
                'is_active',
                'is_published',
                'updated_at',
            ])
            after = {
                'is_active': template.is_active,
                'is_published': template.is_published,
                'version': _version(template.updated_at),
            }
            return MutationOutcome(
                target_type='document_template',
                target_id=str(template.id),
                before=before,
                after=after,
                response_data={'id': template.id, **after},
                metadata={
                    'deactivated_template_ids': deactivated_ids,
                },
            )

        return _action_response(execute_admin_action(
            request=request,
            capability=self.required_capability,
            action='template.publish' if data['publish'] else 'template.unpublish',
            reason=data['reason'],
            idempotency_key=data['idempotency_key'],
            payload=payload,
            callback=mutate,
        ))


class CapabilityAssignmentView(CapabilityView):
    required_capability = AdminCapability.ROOT
    requires_step_up = True

    def post(self, request, user_id):
        serializer = CapabilityAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        payload = {
            'target_type': 'admin_principal',
            'target_id': str(user_id),
            'capabilities': sorted(set(data['capabilities'])),
            'is_active': data['is_active'],
            'expected_version': data['expected_version'],
        }

        def mutate():
            user = get_object_or_404(CustomUser, pk=user_id, is_staff=True)
            principal = AdminPrincipal.objects.select_for_update().filter(
                user=user,
            ).first()
            current_version = str(principal.version) if principal else 'none'
            if current_version != data['expected_version']:
                raise AdminConflict(
                    code='admin_version_conflict',
                    message='Admin principal changed since it was loaded.',
                    details={'current_version': current_version},
                )
            before = (
                {
                    'capabilities': principal.capabilities,
                    'is_active': principal.is_active,
                    'version': principal.version,
                }
                if principal
                else {}
            )
            active_principals = list(
                AdminPrincipal.objects.select_for_update()
                .filter(is_active=True)
                .only('id', 'capabilities')
            )
            removing_last_root = (
                principal is not None
                and principal.is_active
                and AdminCapability.ROOT in principal.capabilities
                and (
                    not data['is_active']
                    or AdminCapability.ROOT not in data['capabilities']
                )
                and not any(
                    AdminCapability.ROOT in item.capabilities
                    for item in active_principals
                    if item.pk != principal.pk
                )
            )
            if removing_last_root:
                raise AdminConflict(
                    code='last_admin_root',
                    message='The last active admin_root cannot be removed.',
                )
            if principal is None:
                principal = AdminPrincipal(
                    user=user,
                    granted_by=request.user,
                )
            else:
                principal.version += 1
            principal.capabilities = sorted(set(data['capabilities']))
            principal.is_active = data['is_active']
            principal.granted_by = request.user
            principal.save()
            after = {
                'capabilities': principal.capabilities,
                'is_active': principal.is_active,
                'version': principal.version,
            }
            return MutationOutcome(
                target_type='admin_principal',
                target_id=str(principal.id),
                before=before,
                after=after,
                response_data={'user_id': user.id, **after},
            )

        return _action_response(execute_admin_action(
            request=request,
            capability=self.required_capability,
            action='admin_principal.assign',
            reason=data['reason'],
            idempotency_key=data['idempotency_key'],
            payload=payload,
            callback=mutate,
        ))
