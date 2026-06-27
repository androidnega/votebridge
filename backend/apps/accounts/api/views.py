from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.accounts.api.serializers import (
    RoleCreateUpdateSerializer,
    RoleSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserStatusSerializer,
    UserUpdateSerializer,
)
from apps.accounts.permissions import CanManageRoles, CanManageUsers
from apps.accounts.services import role_service, user_service


class StandardPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class RoleViewSet(viewsets.ViewSet):
    permission_classes = [CanManageRoles]

    def list(self, request):
        query = request.query_params.get("search")
        is_active = request.query_params.get("is_active")
        is_active_bool = None
        if is_active is not None:
            is_active_bool = is_active.lower() in ("true", "1", "yes")

        roles = role_service.list_roles(query=query, is_active=is_active_bool)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(roles, request)
        serializer = RoleSerializer(page, many=True)
        return paginator.get_paginated_response(
            {"success": True, "data": serializer.data}
        )

    def retrieve(self, request, uuid=None):
        role = role_service.get_role(uuid)
        serializer = RoleSerializer(role)
        return Response({"success": True, "data": serializer.data})

    def create(self, request):
        serializer = RoleCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = role_service.create_role(**serializer.validated_data)
        return Response(
            {"success": True, "data": RoleSerializer(role).data},
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, uuid=None):
        serializer = RoleCreateUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        role = role_service.update_role(uuid, **serializer.validated_data)
        return Response({"success": True, "data": RoleSerializer(role).data})

    def update(self, request, uuid=None):
        serializer = RoleCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role = role_service.update_role(uuid, **serializer.validated_data)
        return Response({"success": True, "data": RoleSerializer(role).data})

    def destroy(self, request, uuid=None):
        role_service.delete_role(uuid)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ViewSet):
    permission_classes = [CanManageUsers]

    def list(self, request):
        query = request.query_params.get("search")
        role_name = request.query_params.get("role")
        is_active = request.query_params.get("is_active")
        is_verified = request.query_params.get("is_verified")

        is_active_bool = _parse_bool(is_active)
        is_verified_bool = _parse_bool(is_verified)

        users = user_service.list_users(
            query=query,
            role_name=role_name,
            is_active=is_active_bool,
            is_verified=is_verified_bool,
        )

        from apps.accounts.models import Role as RoleModel

        role = getattr(request.user, "role", None)
        if role and role.name in {RoleModel.Name.STUDENT, RoleModel.Name.CANDIDATE}:
            users = users.filter(uuid=request.user.uuid)

        paginator = StandardPagination()
        page = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(page, many=True)
        return paginator.get_paginated_response(
            {"success": True, "data": serializer.data}
        )

    def retrieve(self, request, uuid=None):
        user = user_service.get_user(uuid)
        self._check_object_access(request, user)
        serializer = UserSerializer(user)
        return Response({"success": True, "data": serializer.data})

    def create(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self._check_role_assignment(request, serializer.validated_data)
        user = user_service.create_user(serializer.validated_data)
        return Response(
            {"success": True, "data": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, uuid=None):
        user = user_service.get_user(uuid)
        self._check_object_access(request, user)
        serializer = UserUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self._check_role_assignment(request, serializer.validated_data)
        user = user_service.update_user(uuid, serializer.validated_data)
        return Response({"success": True, "data": UserSerializer(user).data})

    def update(self, request, uuid=None):
        user = user_service.get_user(uuid)
        self._check_object_access(request, user)
        serializer = UserUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self._check_role_assignment(request, serializer.validated_data)
        user = user_service.update_user(uuid, serializer.validated_data)
        return Response({"success": True, "data": UserSerializer(user).data})

    def destroy(self, request, uuid=None):
        user_service.delete_user(uuid)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, uuid=None):
        serializer = UserStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_service.get_user(uuid)
        if "is_active" in serializer.validated_data:
            user = user_service.set_active_status(
                uuid, serializer.validated_data["is_active"]
            )
        if "is_verified" in serializer.validated_data:
            user = user_service.set_verified_status(
                uuid, serializer.validated_data["is_verified"]
            )

        return Response({"success": True, "data": UserSerializer(user).data})

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, uuid=None):
        user = user_service.set_active_status(uuid, True)
        return Response({"success": True, "data": UserSerializer(user).data})

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, uuid=None):
        user = user_service.set_active_status(uuid, False)
        return Response({"success": True, "data": UserSerializer(user).data})

    @action(detail=True, methods=["post"], url_path="verify")
    def verify(self, request, uuid=None):
        user = user_service.set_verified_status(uuid, True)
        return Response({"success": True, "data": UserSerializer(user).data})

    @action(detail=True, methods=["post"], url_path="unverify")
    def unverify(self, request, uuid=None):
        user = user_service.set_verified_status(uuid, False)
        return Response({"success": True, "data": UserSerializer(user).data})

    def _check_object_access(self, request, user):
        from apps.accounts.models import Role as RoleModel

        role = getattr(request.user, "role", None)
        if role and role.name in {RoleModel.Name.STUDENT, RoleModel.Name.CANDIDATE}:
            if user.uuid != request.user.uuid:
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied("You can only access your own profile.")

    def _check_role_assignment(self, request, data):
        from apps.accounts.models import Role as RoleModel
        from rest_framework.exceptions import PermissionDenied

        actor_role = getattr(getattr(request.user, "role", None), "name", None)
        if actor_role == RoleModel.Name.SUPER_ADMIN:
            return

        role_name = data.get("role_name")
        role_uuid = data.get("role_uuid")
        if role_name == RoleModel.Name.SUPER_ADMIN:
            raise PermissionDenied("Only Super Admins can assign the Super Admin role.")

        if role_uuid:
            from apps.accounts.repositories.role_repository import RoleRepository

            role = RoleRepository().get_by_uuid(role_uuid)
            if role and role.name == RoleModel.Name.SUPER_ADMIN:
                raise PermissionDenied("Only Super Admins can assign the Super Admin role.")


def _parse_bool(value):
    if value is None:
        return None
    return value.lower() in ("true", "1", "yes")
