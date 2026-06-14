from rest_framework.throttling import UserRateThrottle


class RegistryLookupThrottle(UserRateThrottle):
    scope = 'registry_lookup'
