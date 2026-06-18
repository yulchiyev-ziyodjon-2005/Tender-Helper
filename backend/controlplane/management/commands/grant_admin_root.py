from django.core.management.base import BaseCommand, CommandError

from controlplane.constants import AdminCapability
from controlplane.models import AdminPrincipal
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Bootstrap admin_root for an existing Django superuser.'

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--user-id')
        group.add_argument('--email')
        group.add_argument('--phone-number')

    def handle(self, *args, **options):
        filters = {
            key.replace('-', '_'): value
            for key, value in (
                ('id', options.get('user_id')),
                ('email', options.get('email')),
                ('phone_number', options.get('phone_number')),
            )
            if value
        }
        try:
            user = CustomUser.objects.get(**filters)
        except CustomUser.DoesNotExist as exc:
            raise CommandError('User was not found.') from exc
        if not user.is_staff or not user.is_superuser:
            raise CommandError('admin_root bootstrap requires a superuser.')

        principal, created = AdminPrincipal.objects.get_or_create(
            user=user,
            defaults={
                'capabilities': [AdminCapability.ROOT],
                'granted_by': user,
            },
        )
        if not created and AdminCapability.ROOT not in principal.capabilities:
            principal.capabilities.append(AdminCapability.ROOT)
            principal.version += 1
            principal.is_active = True
            principal.granted_by = user
            principal.save()
        self.stdout.write(self.style.SUCCESS(
            f'admin_root granted to {user.id}.'
        ))
