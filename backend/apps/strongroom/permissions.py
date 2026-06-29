from apps.accounts.permissions import IsSuperAdmin


class CanViewStrongroom(IsSuperAdmin):
    message = "Super Admin access required to view strong room data."


class CanManageStrongroom(IsSuperAdmin):
    message = "Super Admin access required to manage strong room operations."
