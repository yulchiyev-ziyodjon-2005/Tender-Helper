from django.contrib import admin

from .models import CompanyMember, TeamSession


@admin.register(CompanyMember)
class CompanyMemberAdmin(admin.ModelAdmin):
    list_display = ('company', 'user', 'role', 'is_active', 'updated_at')
    list_filter = ('role', 'is_active', 'force_password_change')
    search_fields = ('company__company_name', 'user__email', 'user__full_name')


@admin.register(TeamSession)
class TeamSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'browser', 'last_active_at', 'revoked_at')
    list_filter = ('revoked_at',)
    search_fields = ('user__email', 'token_jti', 'ip_address')
    readonly_fields = ('token_jti', 'created_at', 'last_active_at')
