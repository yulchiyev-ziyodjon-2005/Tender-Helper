"""
TenderHelper — Users Admin Configuration
==========================================
CustomUser modelini admin panelda boshqarish.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin panel uchun CustomUser konfiguratsiyasi."""

    # Ro'yxat ko'rinishi
    list_display = (
        'phone_number',
        'email',
        'full_name',
        'role',
        'auth_provider',
        'is_active',
        'date_joined',
    )
    list_filter = ('role', 'auth_provider', 'is_active', 'is_staff')
    search_fields = ('phone_number', 'email', 'full_name')
    ordering = ('-date_joined',)

    # Tahrirlash formasi
    fieldsets = (
        ('Identifikatsiya', {
            'fields': ('phone_number', 'email', 'full_name')
        }),
        ('Rol va Auth', {
            'fields': ('role', 'auth_provider')
        }),
        ('Huquqlar', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Muhim sanalar', {
            'fields': ('last_login',),
            'classes': ('collapse',),
        }),
    )

    # Yangi foydalanuvchi yaratish formasi
    add_fieldsets = (
        ('Yangi foydalanuvchi', {
            'classes': ('wide',),
            'fields': (
                'phone_number',
                'email',
                'full_name',
                'role',
                'auth_provider',
                'password1',
                'password2',
                'is_active',
                'is_staff',
            ),
        }),
    )
