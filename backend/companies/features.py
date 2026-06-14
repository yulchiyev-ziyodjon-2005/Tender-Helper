from dataclasses import dataclass

from rest_framework.exceptions import PermissionDenied


@dataclass(frozen=True)
class CompanyFeatureAccess:
    official_documents: bool
    official_package_export: bool
    verified_company_badge: bool
    stir_competitor_matching: bool


def get_company_feature_access(profile):
    has_stir = bool(profile and profile.has_stir_identity)
    is_verified = bool(
        has_stir and profile.registry_status == profile.RegistryStatus.VERIFIED
    )
    return CompanyFeatureAccess(
        official_documents=has_stir,
        official_package_export=has_stir,
        verified_company_badge=is_verified,
        stir_competitor_matching=has_stir,
    )


def require_company_stir(profile):
    if profile is None or not profile.has_stir_identity:
        raise PermissionDenied({
            'code': 'stir_required',
            'message': "Bu funksiya uchun kompaniya STIRini qo'shing.",
            'action': 'add_stir',
        })
    return profile
