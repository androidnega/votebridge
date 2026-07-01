import logging

from apps.accounts.models import Role, User
from apps.accounts.repositories.role_repository import RoleRepository
from apps.accounts.repositories.user_repository import UserRepository
from core.exceptions import ConflictError, NotFoundError, ValidationError

logger = logging.getLogger("votebridge")


class UserService:
    """Business logic for user management."""

    def __init__(
        self,
        user_repository: UserRepository | None = None,
        role_repository: RoleRepository | None = None,
    ):
        self.user_repository = user_repository or UserRepository()
        self.role_repository = role_repository or RoleRepository()

    def list_users(
        self,
        query: str | None = None,
        role_name: str | None = None,
        is_active: bool | None = None,
        is_verified: bool | None = None,
    ):
        return self.user_repository.search(
            query=query,
            role_name=role_name,
            is_active=is_active,
            is_verified=is_verified,
        )

    def get_user(self, uuid) -> User:
        user = self.user_repository.get_by_uuid(uuid)
        if not user:
            raise NotFoundError(message="User not found.", code="user_not_found")
        return user

    def create_user(self, data: dict) -> User:
        email = data.get("email")
        if not email:
            raise ValidationError(message="Email is required.", code="email_required")

        if self.user_repository.get_by_email(email):
            raise ConflictError(message="A user with this email already exists.", code="email_exists")

        role = self._resolve_role(data.pop("role_uuid", None), data.pop("role_name", None))

        index_number = data.get("index_number", "")
        if index_number:
            existing = self.user_repository.search(query=index_number).filter(
                index_number=index_number
            )
            if existing.exists():
                raise ConflictError(
                    message="A user with this index number already exists.",
                    code="index_number_exists",
                )

        student_id = data.get("student_id", "")
        if student_id:
            existing = self.user_repository.search(query=student_id).filter(
                student_id=student_id
            )
            if existing.exists():
                raise ConflictError(
                    message="A user with this student ID already exists.",
                    code="student_id_exists",
                )

        password = data.pop("password", None)
        if not password:
            raise ValidationError(message="Password is required.", code="password_required")

        user = self.user_repository.create(role=role, password=password, **data)
        logger.info("User created: %s", user.uuid)
        return user

    def update_user(self, uuid, data: dict) -> User:
        user = self.get_user(uuid)

        if "email" in data and data["email"].lower() != user.email.lower():
            if self.user_repository.get_by_email(data["email"]):
                raise ConflictError(message="A user with this email already exists.", code="email_exists")

        if "role_uuid" in data or "role_name" in data:
            role_uuid = data.pop("role_uuid", None)
            role_name = data.pop("role_name", None)
            data["role"] = self._resolve_role(role_uuid, role_name)

        if "index_number" in data and data["index_number"]:
            existing = self.user_repository.search(query=data["index_number"]).filter(
                index_number=data["index_number"]
            ).exclude(uuid=user.uuid)
            if existing.exists():
                raise ConflictError(
                    message="A user with this index number already exists.",
                    code="index_number_exists",
                )

        if "student_id" in data and data["student_id"]:
            existing = self.user_repository.search(query=data["student_id"]).filter(
                student_id=data["student_id"]
            ).exclude(uuid=user.uuid)
            if existing.exists():
                raise ConflictError(
                    message="A user with this student ID already exists.",
                    code="student_id_exists",
                )

        if "phone_number" in data and data["phone_number"] != user.phone_number:
            from apps.elections.models import Election
            from apps.elections.repositories.eligibility_repository import VoterEligibilityRepository

            has_open = VoterEligibilityRepository().get_queryset().filter(
                user=user,
                is_eligible=True,
                election__status=Election.Status.OPEN,
            ).exists()
            if has_open:
                raise ValidationError(
                    message="Phone number cannot be changed while an election is open.",
                    code="phone_locked",
                )

        password = data.pop("password", None)
        user = self.user_repository.update(user, password=password, **data)
        logger.info("User updated: %s", user.uuid)
        return user

    def delete_user(self, uuid) -> None:
        user = self.get_user(uuid)
        self.user_repository.delete(user)
        logger.info("User deleted: %s", uuid)

    def set_active_status(self, uuid, is_active: bool) -> User:
        user = self.get_user(uuid)
        user = self.user_repository.update(user, is_active=is_active)
        logger.info("User %s active status set to %s", uuid, is_active)
        return user

    def set_verified_status(self, uuid, is_verified: bool) -> User:
        user = self.get_user(uuid)
        user = self.user_repository.update(user, is_verified=is_verified)
        logger.info("User %s verified status set to %s", uuid, is_verified)
        return user

    def _resolve_role(self, role_uuid=None, role_name=None) -> Role:
        if role_uuid:
            role = self.role_repository.get_by_uuid(role_uuid)
            if not role:
                raise NotFoundError(message="Role not found.", code="role_not_found")
            return role

        if role_name:
            role = self.role_repository.get_by_name(role_name)
            if not role:
                raise NotFoundError(message="Role not found.", code="role_not_found")
            return role

        raise ValidationError(message="Role is required.", code="role_required")
