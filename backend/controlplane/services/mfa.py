from django.utils.module_loading import import_string


class AdminMFAProvider:
    def verify(self, *, user, code):
        raise NotImplementedError


class DisabledAdminMFAProvider(AdminMFAProvider):
    def verify(self, *, user, code):
        return False


def get_admin_mfa_provider():
    from django.conf import settings

    provider_class = import_string(settings.ADMIN_MFA_PROVIDER)
    return provider_class()
