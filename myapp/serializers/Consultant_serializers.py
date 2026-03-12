# myapp/serializers/Consultant_serializers.py
from rest_framework import serializers
from myapp.Models.Auth_models import User


class ConsultantCreateStudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    # Show consultant name in response (read only)
    reference_name = serializers.SerializerMethodField(read_only=True)
    assigned_to_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'password',
            'name',
            'father_name',
            'cnic',
            'dob',
            'address',
            'highest_education',
            'phone',
            'email',
            'father_phone',
            'reference',          # FK — accepts consultant ID
            'assigned_to',        # FK — accepts consultant ID
            'reference_name',     # read only — shows consultant name
            'assigned_to_name',   # read only — shows consultant name
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
        validated_data['role'] = User.Role.STUDENT   # always student
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ConsultantUpdateStudentSerializer(serializers.ModelSerializer):
    reference_name = serializers.SerializerMethodField(read_only=True)
    assigned_to_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'name',
            'father_name',
            'cnic',
            'dob',
            'address',
            'highest_education',
            'phone',
            'email',
            'father_phone',
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

    def validate(self, data):
        if self.instance and self.instance.role != User.Role.STUDENT:
            raise serializers.ValidationError("You can only update student accounts.")
        return data