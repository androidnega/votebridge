from django.db.models import Q, QuerySet

from apps.accounts.models import Role


class RoleRepository:
    """Data access layer for Role entities."""

    def get_queryset(self) -> QuerySet[Role]:
        return Role.objects.all()

    def get_by_uuid(self, uuid) -> Role | None:
        return self.get_queryset().filter(uuid=uuid).first()

    def get_by_name(self, name: str) -> Role | None:
        return self.get_queryset().filter(name=name).first()

    def get_by_id(self, role_id: int) -> Role | None:
        return self.get_queryset().filter(pk=role_id).first()

    def create(self, **data) -> Role:
        return Role.objects.create(**data)

    def update(self, role: Role, **data) -> Role:
        for field, value in data.items():
            setattr(role, field, value)
        role.save()
        return role

    def delete(self, role: Role) -> None:
        role.delete()

    def search(self, query: str | None = None, is_active: bool | None = None) -> QuerySet[Role]:
        queryset = self.get_queryset()
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        return queryset
