from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from subscriptions.constants import Feature
from subscriptions.services.entitlements import authorize_feature
from subscriptions.services.membership import (
    accessible_companies,
    resolve_company_membership,
)
from .models import CompanyMember, TeamPermission, TeamSession
from .serializers import (
    CompanyMemberSerializer,
    TeamMemberInviteSerializer,
    TeamMemberUpdateSerializer,
)


def _company_for_user(user, company_id=None):
    companies = accessible_companies(user)
    if company_id:
        return get_object_or_404(companies, pk=company_id)
    return companies.order_by('-created_at').first()


def _require_team_manager(user, company):
    entitlement = authorize_feature(user, company, Feature.TEAM_COLLABORATION)
    membership = resolve_company_membership(user, company)
    if (
        membership.role not in {'owner', 'admin'}
        and TeamPermission.MANAGE_TEAM not in membership.permissions
    ):
        return None
    return entitlement


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def workspace_view(request):
    company = _company_for_user(request.user, request.query_params.get('company_id'))
    if company is None:
        return Response({'code': 'company_required'}, status=status.HTTP_404_NOT_FOUND)
    membership = resolve_company_membership(request.user, company)
    return Response({
        'company': {
            'id': company.id,
            'name': company.company_name,
            'plan': company.current_tariff,
            'stir_verified': company.has_stir_identity,
        },
        'membership': {
            'role': membership.role,
            'permissions': membership.permissions,
            'can_manage_team': (
                membership.role in {'owner', 'admin'}
                or TeamPermission.MANAGE_TEAM in membership.permissions
            ),
        },
        'platform_admin': request.user.is_staff,
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def members_view(request):
    company_id = (
        request.query_params.get('company_id')
        if request.method == 'GET'
        else request.data.get('company_id')
    )
    company = _company_for_user(request.user, company_id)
    if company is None:
        return Response({'code': 'company_required'}, status=status.HTTP_404_NOT_FOUND)
    if _require_team_manager(request.user, company) is None:
        return Response({'code': 'team_permission_denied'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        members = CompanyMember.objects.filter(company=company).select_related('user')
        return Response(CompanyMemberSerializer(members, many=True).data)

    serializer = TeamMemberInviteSerializer(
        data=request.data,
        context={'request': request, 'company': company},
    )
    serializer.is_valid(raise_exception=True)
    member = serializer.save()
    payload = CompanyMemberSerializer(member).data
    payload['temporary_password'] = getattr(member, 'temporary_password', None)
    return Response(payload, status=status.HTTP_201_CREATED)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def member_detail_view(request, pk):
    member = get_object_or_404(
        CompanyMember.objects.select_related('company', 'user'),
        pk=pk,
    )
    if _company_for_user(request.user, str(member.company_id)) is None:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if _require_team_manager(request.user, member.company) is None:
        return Response({'code': 'team_permission_denied'}, status=status.HTTP_403_FORBIDDEN)
    serializer = TeamMemberUpdateSerializer(member, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(CompanyMemberSerializer(member).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def revoke_member_sessions_view(request, pk):
    member = get_object_or_404(
        CompanyMember.objects.select_related('company', 'user'),
        pk=pk,
    )
    if _company_for_user(request.user, str(member.company_id)) is None:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if _require_team_manager(request.user, member.company) is None:
        return Response({'code': 'team_permission_denied'}, status=status.HTTP_403_FORBIDDEN)
    if member.role == CompanyMember.Role.OWNER:
        return Response(
            {'code': 'owner_session_revoke_denied'},
            status=status.HTTP_409_CONFLICT,
        )

    with transaction.atomic():
        user = member.user.__class__.objects.select_for_update().get(pk=member.user_id)
        user.auth_version += 1
        user.save(update_fields=['auth_version', 'updated_at'])
        TeamSession.objects.filter(
            user=user,
            revoked_at__isnull=True,
        ).update(revoked_at=timezone.now())
        member.is_active = False
        member.save(update_fields=['is_active', 'updated_at'])
    return Response({'status': 'terminated'})
