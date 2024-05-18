import yaml
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Initializes the user role and permission models"

    def handle(self, *args, **options):
        with open(f"{settings.APPS_DIR}/permissions.yml") as file:
            role_permissions = yaml.safe_load(file)

        self._create_permissions(role_permissions)
        self._remove_permissions(role_permissions)
        self.stdout.write(self.style.SUCCESS("Successfully initialized user roles and group permissions"))

    def _create_permissions(self, role_permissions):
        for role, permissions in role_permissions.items():
            group, created = Group.objects.get_or_create(name=role)
            for permission_code in permissions:
                try:
                    permission = Permission.objects.get(codename=permission_code)

                except Permission.DoesNotExist:
                    self.stderr.write(self.style.ERROR(f"Permission '{permission_code}' for role '{role}' not found"))
                    exit(1)

                group.permissions.add(permission)

    def _remove_permissions(self, role_permissions):
        for group in Group.objects.all():
            if group.name in role_permissions:
                permissions = role_permissions[group.name]
                for perm in Permission.objects.all():
                    if perm.codename not in permissions:
                        group.permissions.remove(perm)
            else:
                group.delete()
