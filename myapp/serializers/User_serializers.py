# # myapp/serializers/User_serializers.py
# from rest_framework import serializers
# from myapp.Models.Auth_models import User


# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#     reference_name = serializers.SerializerMethodField(read_only=True)
#     assigned_to_name = serializers.SerializerMethodField(read_only=True)
#     profile_picture_url = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = User
#         fields = [
#             'id',
#             'username',
#             'password',
#             'role',
#             'name',
#             'father_name',
#             'cnic',
#             'dob',
#             'address',
#             'highest_education',
#             'phone',
#             'email',
#             'father_phone',
#             'reference',
#             'assigned_to',
#             'reference_name',
#             'assigned_to_name',
#             'profile_picture',        # accepts image file upload
#             'profile_picture_url',    # returns full URL in response
#         ]

#     def get_reference_name(self, obj):
#         return obj.reference.name if obj.reference else None

#     def get_assigned_to_name(self, obj):
#         return obj.assigned_to.name if obj.assigned_to else None

#     def get_profile_picture_url(self, obj):
#         if obj.profile_picture:
#             request = self.context.get('request')
#             if request:
#                 return request.build_absolute_uri(obj.profile_picture.url)
#             return obj.profile_picture.url
#         return None

#     def validate_reference(self, value):
#         if value and value.role != User.Role.CONSULTANT:
#             raise serializers.ValidationError("Reference must be a consultant.")
#         return value

#     def validate_assigned_to(self, value):
#         if value and value.role != User.Role.CONSULTANT:
#             raise serializers.ValidationError("Assigned to must be a consultant.")
#         return value

#     def create(self, validated_data):
#         password = validated_data.pop('password')
#         user = User(**validated_data)
#         user.set_password(password)
#         user.save()
#         return user


# class UserSerializer(serializers.ModelSerializer):
#     reference_name = serializers.SerializerMethodField(read_only=True)
#     assigned_to_name = serializers.SerializerMethodField(read_only=True)
#     profile_picture_url = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = User
#         fields = [
#             'id',
#             'username',
#             'role',
#             'name',
#             'father_name',
#             'cnic',
#             'dob',
#             'address',
#             'highest_education',
#             'phone',
#             'email',
#             'father_phone',
#             'reference',
#             'assigned_to',
#             'reference_name',
#             'assigned_to_name',
#             'profile_picture',
#             'profile_picture_url',
#             'created_at',
#         ]
#         read_only_fields = ['id', 'created_at']

#     def get_reference_name(self, obj):
#         return obj.reference.name if obj.reference else None

#     def get_assigned_to_name(self, obj):
#         return obj.assigned_to.name if obj.assigned_to else None

#     def get_profile_picture_url(self, obj):
#         if obj.profile_picture:
#             request = self.context.get('request')
#             if request:
#                 return request.build_absolute_uri(obj.profile_picture.url)
#             return obj.profile_picture.url
#         return None

#     def validate_reference(self, value):
#         if value and value.role != User.Role.CONSULTANT:
#             raise serializers.ValidationError("Reference must be a consultant.")
#         return value

#     def validate_assigned_to(self, value):
#         if value and value.role != User.Role.CONSULTANT:
#             raise serializers.ValidationError("Assigned to must be a consultant.")
#         return value


# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         email = data.get("email")
#         password = data.get("password")

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             raise serializers.ValidationError("Invalid email or password")

#         if not user.check_password(password):
#             raise serializers.ValidationError("Invalid email or password")

#         data["user"] = user
#         return data



# myapp/serializers/User_serializers.py
from rest_framework import serializers
from myapp.Models.Auth_models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    reference_name = serializers.SerializerMethodField(read_only=True)
    assigned_to_name = serializers.SerializerMethodField(read_only=True)
    profile_picture_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'role', 'name', 'father_name',
            'cnic', 'dob', 'address', 'highest_education', 'phone', 'email',
            'father_phone', 'reference', 'assigned_to',
            'reference_name', 'assigned_to_name',
            'profile_picture', 'profile_picture_url',
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
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    # password is write-only so it's never returned in responses
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    reference_name = serializers.SerializerMethodField(read_only=True)
    assigned_to_name = serializers.SerializerMethodField(read_only=True)
    profile_picture_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'role', 'name', 'father_name',
            'cnic', 'dob', 'address', 'highest_education', 'phone', 'email',
            'father_phone', 'reference', 'assigned_to',
            'reference_name', 'assigned_to_name',
            'profile_picture', 'profile_picture_url',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

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

    def update(self, instance, validated_data):
        # Handle password separately — must be hashed
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


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
