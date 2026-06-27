from rest_framework import serializers

from apps.accounts.models import Role, User


class RoleSerializer(serializers.ModelSerializer):
    name_display = serializers.CharField(source="get_name_display", read_only=True)

    class Meta:
        model = Role
        fields = [
            "uuid",
            "name",
            "name_display",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]


class RoleCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["name", "description", "is_active"]


class UserRoleSerializer(serializers.ModelSerializer):
    name_display = serializers.CharField(source="get_name_display", read_only=True)

    class Meta:
        model = Role
        fields = ["uuid", "name", "name_display"]


class UserSerializer(serializers.ModelSerializer):
    role = UserRoleSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "uuid",
            "role",
            "index_number",
            "student_id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "is_active",
            "is_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class UserCreateSerializer(serializers.Serializer):
    role_uuid = serializers.UUIDField(required=False)
    role_name = serializers.CharField(required=False)
    index_number = serializers.CharField(required=False, allow_blank=True, max_length=50)
    student_id = serializers.CharField(required=False, allow_blank=True, max_length=50)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=20)
    password = serializers.CharField(write_only=True, min_length=8)
    is_active = serializers.BooleanField(default=True)
    is_verified = serializers.BooleanField(default=False)

    def validate(self, attrs):
        if not attrs.get("role_uuid") and not attrs.get("role_name"):
            raise serializers.ValidationError(
                {"role": "Either role_uuid or role_name is required."}
            )
        return attrs


class UserUpdateSerializer(serializers.Serializer):
    role_uuid = serializers.UUIDField(required=False)
    role_name = serializers.CharField(required=False)
    index_number = serializers.CharField(required=False, allow_blank=True, max_length=50)
    student_id = serializers.CharField(required=False, allow_blank=True, max_length=50)
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=20)
    password = serializers.CharField(write_only=True, required=False, min_length=8)
    is_active = serializers.BooleanField(required=False)
    is_verified = serializers.BooleanField(required=False)


class UserStatusSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=False)
    is_verified = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError(
                "At least one of is_active or is_verified is required."
            )
        return attrs
