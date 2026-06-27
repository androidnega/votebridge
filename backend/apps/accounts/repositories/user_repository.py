from django.db.models import Q, QuerySet

from apps.accounts.models import User


class UserRepository:
    """Data access layer for User entities."""

    def get_queryset(self) -> QuerySet[User]:
        return User.objects.select_related("role").all()

    def get_by_uuid(self, uuid) -> User | None:
        return self.get_queryset().filter(uuid=uuid).first()

    def get_by_email(self, email: str) -> User | None:
        return self.get_queryset().filter(email__iexact=email.strip()).first()

    def get_by_username(self, username: str) -> User | None:
        return self.get_queryset().filter(username__iexact=username.strip()).first()

    def get_by_index_number(self, index_number: str) -> User | None:
        normalized = index_number.strip().upper()
        return self.get_queryset().filter(index_number__iexact=normalized).first()

    def create(self, **data) -> User:
        password = data.pop("password", None)
        user = User(**data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, user: User, **data) -> User:
        password = data.pop("password", None)
        for field, value in data.items():
            setattr(user, field, value)
        if password:
            user.set_password(password)
        user.save()
        return user

    def delete(self, user: User) -> None:
        user.delete()

    def search(
        self,
        query: str | None = None,
        role_name: str | None = None,
        is_active: bool | None = None,
        is_verified: bool | None = None,
    ) -> QuerySet[User]:
        queryset = self.get_queryset()

        if role_name:
            queryset = queryset.filter(role__name=role_name)

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        if is_verified is not None:
            queryset = queryset.filter(is_verified=is_verified)

        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
                | Q(index_number__icontains=query)
                | Q(student_id__icontains=query)
                | Q(phone_number__icontains=query)
            )

        return queryset
