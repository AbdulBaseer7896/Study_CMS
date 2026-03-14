# myapp/serializers/Consultant_serializers.py
from rest_framework import serializers
from myapp.Models.Auth_models import User


class ConsultantCreateStudentSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    reference_name = serializers.SerializerMethodField(read_only=True)
    assigned_to_name = serializers.SerializerMethodField(read_only=True)
    profile_picture_url = serializers.SerializerMethodField(read_only=True)

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
            'reference',
            'assigned_to',
            'reference_name',
            'assigned_to_name',
            'profile_picture',
            'profile_picture_url',
        ]

    def get_reference_name(self, obj):
        return obj.reference.name if obj.reference else None

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.name if obj.assigned_to else None

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

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
        validated_data['role'] = User.Role.STUDENT
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ConsultantUpdateStudentSerializer(serializers.ModelSerializer):
    reference_name = serializers.SerializerMethodField(read_only=True)
    assigned_to_name = serializers.SerializerMethodField(read_only=True)
    profile_picture_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
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
            'profile_picture',
            'profile_picture_url',
        ]

    def get_reference_name(self, obj):
        return obj.reference.name if obj.reference else None

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.name if obj.assigned_to else None

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

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