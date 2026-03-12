# myapp/serializers/User_serializers.py
from rest_framework import serializers
from myapp.Models.Auth_models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    # Read-only name fields to show consultant names in response
    reference_name = serializers.SerializerMethodField(read_only=True)
    assigned_to_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'role',

            'name',
            'father_name',
            'cnic',
            'dob',
            'address',
            'highest_education',

            'phone',
            'email',
            'father_phone',

            # New 2 columns
            'reference',
            'assigned_to',
            'reference_name',
            'assigned_to_name',
        ]

    def get_reference_name(self, obj):
        return obj.reference.name if obj.reference else None

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.name if obj.assigned_to else None

    def validate_reference(self, value):
        if value and value.role != User.Role.CONSULTANT:
            raise serializers.ValidationError("Reference must be a consultant.")
        return value

    def validate_assigned_to(self, value):
        if value and value.role != User.Role.CONSULTANT:
            raise serializers.ValidationError("Assigned to must be a consultant.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    reference_name = serializers.SerializerMethodField(read_only=True)
    assigned_to_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'role',

            'name',
            'father_name',
            'cnic',
            'dob',
            'address',
            'highest_education',

            'phone',
            'email',
            'father_phone',

            # New 2 columns
            'reference',
            'assigned_to',
            'reference_name',
            'assigned_to_name',

            'created_at',
        ]

        read_only_fields = ['id', 'created_at']

    def get_reference_name(self, obj):
        return obj.reference.name if obj.reference else None

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.name if obj.assigned_to else None

    def validate_reference(self, value):
        if value and value.role != User.Role.CONSULTANT:
            raise serializers.ValidationError("Reference must be a consultant.")
        return value

    def validate_assigned_to(self, value):
        if value and value.role != User.Role.CONSULTANT:
            raise serializers.ValidationError("Assigned to must be a consultant.")
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")

        data["user"] = user
        return data