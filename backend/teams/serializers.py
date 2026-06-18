import secrets
import string

from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from users.models import CustomUser
from .models import CompanyMember, TeamPermission


def generate_temporary_password(length=16):
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(char.islower() for char in password)
            and any(char.isupper() for char in password)
            and any(char.isdigit() for char in password)
            and any(char in '!@#$%^&*' for char in password)
        ):
            return password


class TeamSessionSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    audience = serializers.CharField()
    auth_version = serializers.IntegerField()
    device = serializers.CharField()
    browser = serializers.CharField()
    ip_address = serializers.IPAddressField(allow_null=True)
    mfa_verified_at = serializers.DateTimeField(allow_null=True)
    expires_at = serializers.DateTimeField(allow_null=True)
    last_active_at = serializers.DateTimeField()
    revoked_at = serializers.DateTimeField(allow_null=True)
    revoked_reason = serializers.CharField()


class CompanyMemberSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    login_status = serializers.SerializerMethodField()
    sessions = serializers.SerializerMethodField()

    class Meta:
        model = CompanyMember
        fields = [
            'id',
            'company_id',
            'user_id',
            'full_name',
            'email',
            'role',
            'permissions',
            'can_search_lots',
            'can_run_ai_analysis',
            'can_generate_documents',
            'can_view_competitor_metrics',
            'force_password_change',
            'is_active',
            'login_status',
            'sessions',
            'created_at',
            'updated_at',
        ]

    def get_login_status(self, obj):
        if not obj.is_active or not obj.user.is_active:
            return 'terminated'
        return (
            'active'
            if obj.user.team_sessions.filter(revoked_at__isnull=True).exists()
            else 'invited'
        )

    def get_sessions(self, obj):
        sessions = obj.user.team_sessions.all()[:5]
        return TeamSessionSerializer(sessions, many=True).data


class TeamMemberInviteSerializer(serializers.Serializer):
    full_name = serializers.CharField(min_length=2, max_length=255)
    email = serializers.EmailField()
    temporary_password = serializers.CharField(
        min_length=12,
        max_length=128,
        required=False,
        allow_blank=True,
    )
    force_password_change = serializers.BooleanField(default=True)
    role = serializers.ChoiceField(
        choices=[
            CompanyMember.Role.ADMIN,
            CompanyMember.Role.MANAGER,
            CompanyMember.Role.ANALYST,
            CompanyMember.Role.VIEWER,
        ],
    )
    permissions = serializers.ListField(
        child=serializers.ChoiceField(choices=TeamPermission.ALL),
        allow_empty=True,
    )

    def validate_email(self, value):
        return CustomUser.objects.normalize_email(value).lower()

    def validate_permissions(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Permissions must be unique.')
        return value

    def validate_temporary_password(self, value):
        if value:
            validate_password(value)
        return value

    @transaction.atomic
    def create(self, validated_data):
        company = self.context['company']
        invited_by = self.context['request'].user
        password = validated_data.pop('temporary_password', '') or generate_temporary_password()
        user, created = CustomUser.objects.get_or_create(
            email=validated_data['email'],
            defaults={
                'full_name': validated_data['full_name'],
                'auth_provider': CustomUser.AuthProvider.EMAIL,
                'is_active': True,
            },
        )
        if created:
            user.set_password(password)
            user.save(update_fields=['password'])
        elif CompanyMember.objects.filter(company=company, user=user).exists():
            raise serializers.ValidationError({
                'email': 'This employee already belongs to the company.',
            })

        member = CompanyMember.objects.create(
            company=company,
            user=user,
            role=validated_data['role'],
            permissions=validated_data['permissions'],
            force_password_change=validated_data['force_password_change'],
            invited_by=invited_by,
        )
        member.temporary_password = password if created else None
        return member


class TeamMemberUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyMember
        fields = ['role', 'permissions', 'force_password_change', 'is_active']

    def validate_role(self, value):
        if (
            self.instance.role == CompanyMember.Role.OWNER
            and value != CompanyMember.Role.OWNER
        ):
            raise serializers.ValidationError('Company owner role cannot be changed.')
        return value

    def validate_permissions(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Permissions must be unique.')
        return value
