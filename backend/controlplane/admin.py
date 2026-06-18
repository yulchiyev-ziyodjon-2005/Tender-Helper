from django.contrib import admin

from controlplane.models import (
    AdminActionRequest,
    AdminAuditEvent,
    AdminPrincipal,
    FeatureFlag,
    InvariantDiagnosticCounter,
    SystemSetting,
)


@admin.register(AdminPrincipal)
class AdminPrincipalAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'version', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('user__email', 'user__phone_number', 'user__full_name')
    readonly_fields = ('mfa_verified_at', 'step_up_at', 'created_at', 'updated_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AdminActionRequest)
class AdminActionRequestAdmin(admin.ModelAdmin):
    list_display = ('actor', 'action', 'status', 'created_at')
    list_filter = ('status', 'action')
    search_fields = ('actor__email', 'idempotency_key')
    readonly_fields = (
        'actor',
        'idempotency_key',
        'action',
        'request_hash',
        'status',
        'response_data',
        'response_status',
        'created_at',
        'updated_at',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AdminAuditEvent)
class AdminAuditEventAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'actor',
        'capability',
        'action',
        'target_type',
        'outcome',
    )
    list_filter = ('capability', 'action', 'outcome')
    search_fields = ('actor__email', 'target_id', 'reason', 'request_id')
    readonly_fields = (
        'actor',
        'capability',
        'action',
        'target_type',
        'target_id',
        'reason',
        'before',
        'after',
        'outcome',
        'request_id',
        'ip_address',
        'metadata',
        'created_at',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ('feature', 'is_enabled', 'version', 'updated_at')
    list_filter = ('is_enabled',)
    readonly_fields = ('feature', 'version', 'updated_by', 'updated_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'version', 'updated_at')
    readonly_fields = ('key', 'version', 'updated_by', 'updated_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(InvariantDiagnosticCounter)
class InvariantDiagnosticCounterAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'source_status', 'observed_at', 'updated_at')
    list_filter = ('source_status',)
    search_fields = ('key', 'diagnostic_message')
    readonly_fields = (
        'key',
        'value',
        'source_status',
        'dimensions',
        'diagnostic_message',
        'observed_at',
        'updated_at',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
