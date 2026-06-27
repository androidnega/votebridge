from rest_framework.permissions import BasePermission

from apps.accounts.permissions import IsAdminOrSuperAdmin


class CanViewStrongroom(IsAdminOrSuperAdmin):
    message = "Admin access required to view strongroom data."


class CanManageStrongroom(IsAdminOrSuperAdmin):
    message = "Admin access required to manage strongroom operations."
