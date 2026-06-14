from django.db import transaction

from companies.models import CompanyProfile


class ProfileStateError(Exception):
    code = 'invalid_profile_state'
    public_message = 'Company profile state does not allow this operation'


class ExistingStirError(ProfileStateError):
    code = 'stir_already_present'
    public_message = 'Remove or refresh the existing STIR instead of skipping it'


@transaction.atomic
def skip_stir_onboarding(user, profile_data):
    profile = (
        CompanyProfile.objects.select_for_update()
        .filter(user=user)
        .order_by('-created_at')
        .first()
    )
    if profile is not None and profile.stir:
        raise ExistingStirError()
    if profile is None:
        profile = CompanyProfile(user=user)

    editable_fields = {
        'company_name',
        'company_type',
        'industry',
        'experience_level',
        'director_name',
        'legal_address',
        'registration_date',
        'has_vat',
        'onboarding_answers',
    }
    for field, value in profile_data.items():
        if field in editable_fields:
            setattr(profile, field, value)

    profile.stir = None
    profile.stir_skipped = True
    profile.registry_source = CompanyProfile.RegistrySource.MANUAL
    profile.registry_status = CompanyProfile.RegistryStatus.MANUAL
    profile.registry_fetched_at = None
    profile.raw_tax_data = {}
    profile.full_clean()
    profile.save()
    return profile
