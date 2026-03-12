# myapp/serializers/Document_serializers.py
from rest_framework import serializers
from myapp.Models.Document_models import (
    StudentDocument, ExperienceLetter,
    ReferenceLetter, OtherDocument
)


# ── Shared URL helper ─────────────────────────────────────────────────
def get_file_url(obj_file, request):
    if obj_file:
        try:
            url = obj_file.url
            if request:
                return request.build_absolute_uri(url)
            return url
        except Exception:
            return None
    return None


# ════════════════════════════════════════════════════════════════════
#  IDENTITY DOCUMENTS
# ════════════════════════════════════════════════════════════════════
class IdentityDocumentSerializer(serializers.ModelSerializer):

    # File URL fields (read only)
    cnic_front_url          = serializers.SerializerMethodField()
    cnic_back_url           = serializers.SerializerMethodField()
    father_cnic_front_url   = serializers.SerializerMethodField()
    father_cnic_back_url    = serializers.SerializerMethodField()
    passport_page1_url      = serializers.SerializerMethodField()
    passport_page2_url      = serializers.SerializerMethodField()
    b_form_front_url        = serializers.SerializerMethodField()
    b_form_back_url         = serializers.SerializerMethodField()
    domicile_url            = serializers.SerializerMethodField()

    class Meta:
        model = StudentDocument
        fields = [
            'id', 'student',
            # CNIC
            'cnic_front',           'cnic_front_url',
            'cnic_back',            'cnic_back_url',
            # Father CNIC
            'father_cnic_front',    'father_cnic_front_url',
            'father_cnic_back',     'father_cnic_back_url',
            # Passport
            'passport_page1',       'passport_page1_url',
            'passport_page2',       'passport_page2_url',
            # B-Form
            'b_form_front',         'b_form_front_url',
            'b_form_back',          'b_form_back_url',
            # Domicile
            'domicile',             'domicile_url',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']

    def get_cnic_front_url(self, obj):         return get_file_url(obj.cnic_front, self.context.get('request'))
    def get_cnic_back_url(self, obj):          return get_file_url(obj.cnic_back, self.context.get('request'))
    def get_father_cnic_front_url(self, obj):  return get_file_url(obj.father_cnic_front, self.context.get('request'))
    def get_father_cnic_back_url(self, obj):   return get_file_url(obj.father_cnic_back, self.context.get('request'))
    def get_passport_page1_url(self, obj):     return get_file_url(obj.passport_page1, self.context.get('request'))
    def get_passport_page2_url(self, obj):     return get_file_url(obj.passport_page2, self.context.get('request'))
    def get_b_form_front_url(self, obj):       return get_file_url(obj.b_form_front, self.context.get('request'))
    def get_b_form_back_url(self, obj):        return get_file_url(obj.b_form_back, self.context.get('request'))
    def get_domicile_url(self, obj):           return get_file_url(obj.domicile, self.context.get('request'))


# ════════════════════════════════════════════════════════════════════
#  MATRIC DOCUMENTS (9 & 10)
# ════════════════════════════════════════════════════════════════════
class MatricDocumentSerializer(serializers.ModelSerializer):
    matric_degree_front_url      = serializers.SerializerMethodField()
    matric_degree_back_url       = serializers.SerializerMethodField()
    matric_result_card_front_url = serializers.SerializerMethodField()
    matric_result_card_back_url  = serializers.SerializerMethodField()

    class Meta:
        model = StudentDocument
        fields = [
            'id', 'student',
            'matric_degree_front',          'matric_degree_front_url',
            'matric_degree_back',           'matric_degree_back_url',
            'matric_result_card_front',     'matric_result_card_front_url',
            'matric_result_card_back',      'matric_result_card_back_url',
            'matric_institute',
            'matric_year',
            'matric_description',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']

    def get_matric_degree_front_url(self, obj):      return get_file_url(obj.matric_degree_front, self.context.get('request'))
    def get_matric_degree_back_url(self, obj):       return get_file_url(obj.matric_degree_back, self.context.get('request'))
    def get_matric_result_card_front_url(self, obj): return get_file_url(obj.matric_result_card_front, self.context.get('request'))
    def get_matric_result_card_back_url(self, obj):  return get_file_url(obj.matric_result_card_back, self.context.get('request'))


# ════════════════════════════════════════════════════════════════════
#  INTER DOCUMENTS (11 & 12)
# ════════════════════════════════════════════════════════════════════
class InterDocumentSerializer(serializers.ModelSerializer):
    inter_degree_front_url      = serializers.SerializerMethodField()
    inter_degree_back_url       = serializers.SerializerMethodField()
    inter_result_card_front_url = serializers.SerializerMethodField()
    inter_result_card_back_url  = serializers.SerializerMethodField()

    class Meta:
        model = StudentDocument
        fields = [
            'id', 'student',
            'inter_degree_front',           'inter_degree_front_url',
            'inter_degree_back',            'inter_degree_back_url',
            'inter_result_card_front',      'inter_result_card_front_url',
            'inter_result_card_back',       'inter_result_card_back_url',
            'inter_institute',
            'inter_year',
            'inter_description',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']

    def get_inter_degree_front_url(self, obj):      return get_file_url(obj.inter_degree_front, self.context.get('request'))
    def get_inter_degree_back_url(self, obj):       return get_file_url(obj.inter_degree_back, self.context.get('request'))
    def get_inter_result_card_front_url(self, obj): return get_file_url(obj.inter_result_card_front, self.context.get('request'))
    def get_inter_result_card_back_url(self, obj):  return get_file_url(obj.inter_result_card_back, self.context.get('request'))


# ════════════════════════════════════════════════════════════════════
#  BS DOCUMENTS
# ════════════════════════════════════════════════════════════════════
class BSDocumentSerializer(serializers.ModelSerializer):
    bs_degree_front_url     = serializers.SerializerMethodField()
    bs_degree_back_url      = serializers.SerializerMethodField()
    bs_transcript_front_url = serializers.SerializerMethodField()
    bs_transcript_back_url  = serializers.SerializerMethodField()

    class Meta:
        model = StudentDocument
        fields = [
            'id', 'student',
            'bs_degree_front',      'bs_degree_front_url',
            'bs_degree_back',       'bs_degree_back_url',
            'bs_transcript_front',  'bs_transcript_front_url',
            'bs_transcript_back',   'bs_transcript_back_url',
            'bs_institute',
            'bs_year',
            'bs_description',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']

    def get_bs_degree_front_url(self, obj):     return get_file_url(obj.bs_degree_front, self.context.get('request'))
    def get_bs_degree_back_url(self, obj):      return get_file_url(obj.bs_degree_back, self.context.get('request'))
    def get_bs_transcript_front_url(self, obj): return get_file_url(obj.bs_transcript_front, self.context.get('request'))
    def get_bs_transcript_back_url(self, obj):  return get_file_url(obj.bs_transcript_back, self.context.get('request'))


# ════════════════════════════════════════════════════════════════════
#  MS DOCUMENTS
# ════════════════════════════════════════════════════════════════════
class MSDocumentSerializer(serializers.ModelSerializer):
    ms_degree_front_url     = serializers.SerializerMethodField()
    ms_degree_back_url      = serializers.SerializerMethodField()
    ms_transcript_front_url = serializers.SerializerMethodField()
    ms_transcript_back_url  = serializers.SerializerMethodField()

    class Meta:
        model = StudentDocument
        fields = [
            'id', 'student',
            'ms_degree_front',      'ms_degree_front_url',
            'ms_degree_back',       'ms_degree_back_url',
            'ms_transcript_front',  'ms_transcript_front_url',
            'ms_transcript_back',   'ms_transcript_back_url',
            'ms_institute',
            'ms_year',
            'ms_description',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']

    def get_ms_degree_front_url(self, obj):     return get_file_url(obj.ms_degree_front, self.context.get('request'))
    def get_ms_degree_back_url(self, obj):      return get_file_url(obj.ms_degree_back, self.context.get('request'))
    def get_ms_transcript_front_url(self, obj): return get_file_url(obj.ms_transcript_front, self.context.get('request'))
    def get_ms_transcript_back_url(self, obj):  return get_file_url(obj.ms_transcript_back, self.context.get('request'))


# ════════════════════════════════════════════════════════════════════
#  PROFESSIONAL DOCUMENTS
# ════════════════════════════════════════════════════════════════════
class ProfessionalDocumentSerializer(serializers.ModelSerializer):
    cv_url       = serializers.SerializerMethodField()
    ielts_pte_url = serializers.SerializerMethodField()

    class Meta:
        model = StudentDocument
        fields = [
            'id', 'student',
            'cv',               'cv_url',
            'ielts_pte',        'ielts_pte_url',
            'ielts_pte_year',
            'ielts_pte_description',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']

    def get_cv_url(self, obj):        return get_file_url(obj.cv, self.context.get('request'))
    def get_ielts_pte_url(self, obj): return get_file_url(obj.ielts_pte, self.context.get('request'))


# ════════════════════════════════════════════════════════════════════
#  MULTIPLE DOCUMENT SERIALIZERS
# ════════════════════════════════════════════════════════════════════
class ExperienceLetterSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ExperienceLetter
        fields = ['id', 'student', 'file', 'file_url', 'organization', 'year', 'description', 'created_at']
        read_only_fields = ['id', 'uploaded_by', 'created_at']

    def get_file_url(self, obj): return get_file_url(obj.file, self.context.get('request'))


class ReferenceLetterSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ReferenceLetter
        fields = ['id', 'student', 'file', 'file_url', 'referee_name', 'year', 'description', 'created_at']
        read_only_fields = ['id', 'uploaded_by', 'created_at']

    def get_file_url(self, obj): return get_file_url(obj.file, self.context.get('request'))


class OtherDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = OtherDocument
        fields = ['id', 'student', 'file', 'file_url', 'document_name', 'year', 'description', 'created_at']
        read_only_fields = ['id', 'uploaded_by', 'created_at']

    def get_file_url(self, obj): return get_file_url(obj.file, self.context.get('request'))


# ════════════════════════════════════════════════════════════════════
#  FULL STUDENT DOCUMENTS VIEW
# ════════════════════════════════════════════════════════════════════
class StudentAllDocumentsSerializer(serializers.ModelSerializer):
    """Used for GET all documents of a student"""
    identity    = serializers.SerializerMethodField()
    matric      = serializers.SerializerMethodField()
    inter       = serializers.SerializerMethodField()
    bs          = serializers.SerializerMethodField()
    ms          = serializers.SerializerMethodField()
    professional = serializers.SerializerMethodField()

    class Meta:
        model = StudentDocument
        fields = ['id', 'identity', 'matric', 'inter', 'bs', 'ms', 'professional', 'updated_at']

    def get_identity(self, obj):
        return IdentityDocumentSerializer(obj, context=self.context).data

    def get_matric(self, obj):
        return MatricDocumentSerializer(obj, context=self.context).data

    def get_inter(self, obj):
        return InterDocumentSerializer(obj, context=self.context).data

    def get_bs(self, obj):
        return BSDocumentSerializer(obj, context=self.context).data

    def get_ms(self, obj):
        return MSDocumentSerializer(obj, context=self.context).data

    def get_professional(self, obj):
        return ProfessionalDocumentSerializer(obj, context=self.context).data