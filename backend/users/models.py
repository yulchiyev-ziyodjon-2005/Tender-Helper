"""
TenderHelper — CustomUser Model
=================================
UUID asosidagi xavfsiz foydalanuvchi modeli.
Phone + OTP va Google OAuth orqali autentifikatsiya.
"""

import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom manager: email o'rniga phone_number asosiy identifikator.
    """

    def create_user(self, phone_number=None, email=None, password=None, **extra_fields):
        """Oddiy foydalanuvchi yaratish."""
        if not phone_number and not email:
            raise ValueError("Telefon raqami yoki email kiritilishi shart.")

        if email:
            email = self.normalize_email(email)

        extra_fields.setdefault('is_active', True)
        user = self.model(
            phone_number=phone_number,
            email=email,
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number=None, email=None, password=None, **extra_fields):
        """Admin foydalanuvchi yaratish."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser uchun is_staff=True bo'lishi shart.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser uchun is_superuser=True bo'lishi shart.")

        return self.create_user(
            phone_number=phone_number,
            email=email,
            password=password,
            **extra_fields
        )


class CustomUser(AbstractUser):
    """
    TenderHelper foydalanuvchi modeli.
    UUID PK, telefon raqami va Google OAuth qo'llab-quvvatlash.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        USER = 'user', 'Foydalanuvchi'
        MANAGER = 'manager', 'Menejer'
        VIEWER = 'viewer', 'Kuzatuvchi'

    class AuthProvider(models.TextChoices):
        PHONE = 'phone', 'Telefon + OTP'
        GOOGLE = 'google', 'Google OAuth'
        EMAIL = 'email', 'Email + Parol'

    # AbstractUser dan username ni olib tashlaymiz
    username = None

    # Primary Key — UUID
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID"
    )

    # Asosiy identifikatorlar
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Telefon raqami",
        help_text="O'zbekiston formati: +998901234567"
    )

    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
        verbose_name="Email"
    )

    full_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name="To'liq ism"
    )

    # Rol va autentifikatsiya turi
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        verbose_name="Rol"
    )

    auth_provider = models.CharField(
        max_length=20,
        choices=AuthProvider.choices,
        default=AuthProvider.PHONE,
        verbose_name="Auth usuli"
    )

    # Vaqt belgilari
    date_joined = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ro'yxatdan o'tgan sana"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Yangilangan sana"
    )

    # Manager
    objects = CustomUserManager()

    # Login identifikatori
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email']

    class Meta:
        db_table = 'users'
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'
        ordering = ['-date_joined']

    def __str__(self):
        return self.full_name or self.phone_number or self.email or str(self.id)

    @property
    def display_name(self):
        """Foydalanuvchining ko'rsatiladigan ismi."""
        if self.full_name:
            return self.full_name
        if self.phone_number:
            return self.phone_number
        return self.email or 'Noma\'lum'
