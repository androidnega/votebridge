import logging

from apps.accounts.models import Role
from apps.accounts.repositories.role_repository import RoleRepository
from core.exceptions import ConflictError, NotFoundError, ValidationError

logger = logging.getLogger("votebridge")


class RoleService:
    """Business logic for role management."""

    def __init__(self, repository: RoleRepository | None = None):
        self.repository = repository or RoleRepository()

    def list_roles(self, query: str | None = None, is_active: bool | None = None):
        return self.repository.search(query=query, is_active=is_active)

    def get_role(self, uuid) -> Role:
        role = self.repository.get_by_uuid(uuid)
        if not role:
            raise NotFoundError(message="Role not found.", code="role_not_found")
        return role

    def create_role(self, name: str, description: str = "", is_active: bool = True) -> Role:
        if self.repository.get_by_name(name):
            raise ConflictError(message="A role with this name already exists.", code="role_exists")

        if name not in Role.Name.values:
            raise ValidationError(message="Invalid role name.", code="invalid_role_name")

        role = self.repository.create(
            name=name,
            description=description,
            is_active=is_active,
        )
        logger.info("Role created: %s", role.name)
        return role

    def update_role(self, uuid, **data) -> Role:
        role = self.get_role(uuid)

        if "name" in data and data["name"] != role.name:
            if self.repository.get_by_name(data["name"]):
                raise ConflictError(message="A role with this name already exists.", code="role_exists")
            if data["name"] not in Role.Name.values:
                raise ValidationError(message="Invalid role name.", code="invalid_role_name")

        role = self.repository.update(role, **data)
        logger.info("Role updated: %s", role.uuid)
        return role

    def delete_role(self, uuid) -> None:
        role = self.get_role(uuid)
        if role.users.exists():
            raise ConflictError(
                message="Cannot delete a role that is assigned to users.",
                code="role_in_use",
            )
        self.repository.delete(role)
        logger.info("Role deleted: %s", uuid)
