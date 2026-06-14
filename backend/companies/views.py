from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    permission_classes,
    throttle_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CompanyProfile, CompanyRegistryDraft
from .serializers import (
    CompanyProfileSerializer,
    OnboardingSerializer,
    RegistryConfirmSerializer,
    RegistryDraftSerializer,
    RegistryLookupSerializer,
    SkipStirSerializer,
)
from .services.profiles import (
    ExistingStirError,
    skip_stir_onboarding,
)
from .services.registry import (
    DraftExpiredError,
    DraftStateError,
    confirm_registry_draft,
    create_registry_draft,
    expire_registry_draft,
)
from .throttles import RegistryLookupThrottle


def _get_current_profile(user):
    return CompanyProfile.objects.filter(user=user).order_by('-created_at').first()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def onboarding_view(request):
    """
    POST /api/v1/company/onboarding/
    Kompaniya profili va onboarding javoblarini saqlash.
    """
    profile = _get_current_profile(request.user)
    serializer = OnboardingSerializer(
        profile,
        data=request.data,
        partial=profile is not None,
    )
    serializer.is_valid(raise_exception=True)
    profile = serializer.save(user=request.user)
    return Response(CompanyProfileSerializer(profile).data, status=status.HTTP_200_OK)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    GET/PATCH /api/v1/company/profile/
    Joriy foydalanuvchining asosiy kompaniya profili.
    """
    profile = _get_current_profile(request.user)

    if profile is None and request.method == 'GET':
        return Response(
            {
                'error': 'profile_not_found',
                'message': 'Kompaniya profili hali yaratilmagan',
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        return Response(CompanyProfileSerializer(profile).data)

    serializer = CompanyProfileSerializer(
        profile,
        data=request.data,
        partial=profile is not None,
    )
    serializer.is_valid(raise_exception=True)
    serializer.save(user=request.user)
    return Response(serializer.data, status=status.HTTP_200_OK if profile else status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([RegistryLookupThrottle])
def registry_lookup_view(request):
    serializer = RegistryLookupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    profile = _get_current_profile(request.user)
    draft = create_registry_draft(
        request.user,
        serializer.validated_data['stir'],
        profile=profile,
    )
    return Response(
        RegistryDraftSerializer(draft).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def registry_draft_view(request, pk):
    draft = get_object_or_404(
        CompanyRegistryDraft.objects.filter(user=request.user),
        id=pk,
    )
    expire_registry_draft(draft)
    return Response(RegistryDraftSerializer(draft).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def registry_draft_confirm_view(request, pk):
    draft = get_object_or_404(
        CompanyRegistryDraft.objects.filter(user=request.user),
        id=pk,
    )
    serializer = RegistryConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        confirmed_draft = confirm_registry_draft(
            request.user,
            draft.id,
            serializer.validated_data,
        )
    except DraftExpiredError as exc:
        CompanyRegistryDraft.objects.filter(
            user=request.user,
            id=draft.id,
        ).update(
            status=CompanyRegistryDraft.Status.EXPIRED,
            updated_at=timezone.now(),
        )
        return Response(
            {'error': exc.code, 'message': exc.public_message},
            status=status.HTTP_409_CONFLICT,
        )
    except DraftStateError as exc:
        return Response(
            {'error': exc.code, 'message': exc.public_message},
            status=status.HTTP_409_CONFLICT,
        )
    if confirmed_draft is None:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response({
        'draft': RegistryDraftSerializer(confirmed_draft).data,
        'profile': CompanyProfileSerializer(confirmed_draft.profile).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def skip_stir_view(request):
    profile = _get_current_profile(request.user)
    profile_exists = profile is not None
    serializer = SkipStirSerializer(
        data=request.data,
        context={'profile': profile},
        partial=profile is not None,
    )
    serializer.is_valid(raise_exception=True)
    try:
        profile = skip_stir_onboarding(
            request.user,
            serializer.validated_data,
        )
    except ExistingStirError as exc:
        return Response(
            {'error': exc.code, 'message': exc.public_message},
            status=status.HTTP_409_CONFLICT,
        )
    return Response(
        CompanyProfileSerializer(profile).data,
        status=status.HTTP_200_OK if profile_exists else status.HTTP_201_CREATED,
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([RegistryLookupThrottle])
def registry_refresh_view(request):
    profile = _get_current_profile(request.user)
    if profile is None:
        return Response(
            {
                'error': 'profile_not_found',
                'message': 'Kompaniya profili hali yaratilmagan',
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    if not profile.stir:
        return Response(
            {
                'error': 'stir_required',
                'message': "Registry refresh uchun kompaniya STIRini qo'shing",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    draft = create_registry_draft(
        request.user,
        profile.stir,
        profile=profile,
        force_refresh=True,
    )
    return Response(
        RegistryDraftSerializer(draft).data,
        status=status.HTTP_201_CREATED,
    )
