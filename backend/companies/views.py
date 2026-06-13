from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CompanyProfile
from .serializers import CompanyProfileSerializer, OnboardingSerializer


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
