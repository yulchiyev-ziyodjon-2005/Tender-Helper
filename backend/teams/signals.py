from django.db.models.signals import post_save
from django.dispatch import receiver

from companies.models import CompanyProfile
from .models import CompanyMember, ROLE_DEFAULT_PERMISSIONS


@receiver(post_save, sender=CompanyProfile)
def ensure_owner_membership(sender, instance, raw=False, **kwargs):
    if raw:
        return

    CompanyMember.objects.get_or_create(
        company=instance,
        user=instance.user,
        defaults={
            'role': CompanyMember.Role.OWNER,
            'permissions': ROLE_DEFAULT_PERMISSIONS[CompanyMember.Role.OWNER],
            'force_password_change': False,
            'is_active': True,
        },
    )
