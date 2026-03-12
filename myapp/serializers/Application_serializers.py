# myapp/serializers/Application_serializers.py
from rest_framework import serializers
from myapp.Models.Application_models import Application, ApplicationModule, ApplicationImage
from myapp.Models.Auth_models import User


# ── Helper ────────────────────────────────────────────────────────────
def get_file_url(file_field, request):
    if file_field:
        try:
            url = file_field.url
            return request.build_absolute_uri(url) if request else url
        except Exception:
            return None
    return None


# ════════════════════════════════════════════════════════════════════
#  MODULE SERIALIZER
# ════════════════════════════════════════════════════════════════════
class ApplicationModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationModule
        fields = ['id', 'module_name', 'description']


# ════════════════════════════════════════════════════════════════════
#  EXTRA IMAGE SERIALIZER
# ════════════════════════════════════════════════════════════════════
class ApplicationImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ApplicationImage
        fields = ['id', 'image', 'image_url', 'caption', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_image_url(self, obj):
        return get_file_url(obj.image, self.context.get('request'))


# ════════════════════════════════════════════════════════════════════
#  APPLICATION CREATE SERIALIZER
# ════════════════════════════════════════════════════════════════════
class ApplicationCreateSerializer(serializers.ModelSerializer):
    # Accept modules as nested list on create
    modules = ApplicationModuleSerializer(many=True, required=False)

    class Meta:
        model = Application
        fields = [
            'id',
            'student',
            # University
            'application_name',
            'country',
            'university',
            'city',
            'university_portal_link',
            'portal_login_id',
            'portal_login_password',
            # Course
            'degree_name',
            'course_title',
            'modules',
            # Fees
            'apply_fee',
            'yearly_fee',
            # Dates
            'last_date_to_apply',
            'last_date_fee_submit',
            'expected_offer_date',
            # Status & Docs
            'status',
            'offer_letter',
            'fee_slip',
        ]
        read_only_fields = ['id']

    def validate_student(self, value):
        if value.role != User.Role.STUDENT:
            raise serializers.ValidationError("Selected user is not a student.")
        return value

    def create(self, validated_data):
        modules_data = validated_data.pop('modules', [])
        application = Application.objects.create(**validated_data)

        # Create modules
        for module in modules_data:
            ApplicationModule.objects.create(application=application, **module)

        return application


# ════════════════════════════════════════════════════════════════════
#  APPLICATION UPDATE SERIALIZER
# ════════════════════════════════════════════════════════════════════
class ApplicationUpdateSerializer(serializers.ModelSerializer):
    offer_letter_url    = serializers.SerializerMethodField()
    fee_slip_url        = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id',
            # University
            'application_name',
            'country',
            'university',
            'city',
            'university_portal_link',
            'portal_login_id',
            'portal_login_password',
            # Course
            'degree_name',
            'course_title',
            # Fees
            'apply_fee',
            'yearly_fee',
            # Dates
            'last_date_to_apply',
            'last_date_fee_submit',
            'expected_offer_date',
            # Status & Docs
            'status',
            'offer_letter',         'offer_letter_url',
            'fee_slip',             'fee_slip_url',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']

    def get_offer_letter_url(self, obj):
        return get_file_url(obj.offer_letter, self.context.get('request'))

    def get_fee_slip_url(self, obj):
        return get_file_url(obj.fee_slip, self.context.get('request'))


# ════════════════════════════════════════════════════════════════════
#  APPLICATION DETAIL SERIALIZER (GET)
# ════════════════════════════════════════════════════════════════════
class ApplicationDetailSerializer(serializers.ModelSerializer):
    modules         = ApplicationModuleSerializer(many=True, read_only=True)
    extra_images    = ApplicationImageSerializer(many=True, read_only=True)
    offer_letter_url = serializers.SerializerMethodField()
    fee_slip_url    = serializers.SerializerMethodField()
    student_name    = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id',
            'student',          'student_name',
            'created_by_name',
            # University
            'application_name',
            'country',
            'university',
            'city',
            'university_portal_link',
            'portal_login_id',
            'portal_login_password',
            # Course
            'degree_name',
            'course_title',
            'modules',
            # Fees
            'apply_fee',
            'yearly_fee',
            # Dates
            'last_date_to_apply',
            'last_date_fee_submit',
            'expected_offer_date',
            # Status & Docs
            'status',
            'offer_letter',         'offer_letter_url',
            'fee_slip',             'fee_slip_url',
            'extra_images',
            'created_at',
            'updated_at',
        ]

    def get_offer_letter_url(self, obj):
        return get_file_url(obj.offer_letter, self.context.get('request'))

    def get_fee_slip_url(self, obj):
        return get_file_url(obj.fee_slip, self.context.get('request'))

    def get_student_name(self, obj):
        return obj.student.name if obj.student else None

    def get_created_by_name(self, obj):
        return obj.created_by.name if obj.created_by else None


# ════════════════════════════════════════════════════════════════════
#  APPLICATION LIST SERIALIZER
# ════════════════════════════════════════════════════════════════════
class ApplicationListSerializer(serializers.ModelSerializer):
    student_name    = serializers.SerializerMethodField()
    modules_count   = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id',
            'student',          
            'student_name',
            'application_name',
            'country',
            'university',
            'degree_name',
            'course_title',
            'modules_count',
            'status',
            'last_date_to_apply',
            'expected_offer_date',
            'created_at',
        ]

    def get_student_name(self, obj):
        return obj.student.name if obj.student else None

    def get_modules_count(self, obj):
        return obj.modules.count()