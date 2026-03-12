# myapp/Models/Document_models.py
from django.db import models
from myapp.Models.Auth_models import User


class StudentDocument(models.Model):
    """Single model for ALL student documents — grouped by category"""

    student = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='documents',
        limit_choices_to={'role': 'student'}
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents'
    )

    # ── IDENTITY DOCUMENTS ────────────────────────────────────────────
    cnic_front          = models.FileField(upload_to='study_cms/identity/', null=True, blank=True)
    cnic_back           = models.FileField(upload_to='study_cms/identity/', null=True, blank=True)
    father_cnic_front   = models.FileField(upload_to='study_cms/identity/', null=True, blank=True)
    father_cnic_back    = models.FileField(upload_to='study_cms/identity/', null=True, blank=True)
    passport_page1      = models.FileField(upload_to='study_cms/identity/', null=True, blank=True)
    passport_page2      = models.FileField(upload_to='study_cms/identity/', null=True, blank=True)
    b_form_front        = models.FileField(upload_to='study_cms/identity/', null=True, blank=True)
    b_form_back         = models.FileField(upload_to='study_cms/identity/', null=True, blank=True)
    domicile            = models.FileField(upload_to='study_cms/identity/', null=True, blank=True)

    # ── MATRIC DOCUMENTS (9 & 10) ─────────────────────────────────────
    matric_degree_front       = models.FileField(upload_to='study_cms/matric/', null=True, blank=True)
    matric_degree_back        = models.FileField(upload_to='study_cms/matric/', null=True, blank=True)
    matric_result_card_front  = models.FileField(upload_to='study_cms/matric/', null=True, blank=True)
    matric_result_card_back   = models.FileField(upload_to='study_cms/matric/', null=True, blank=True)
    matric_institute          = models.CharField(max_length=255, blank=True, null=True)
    matric_year               = models.CharField(max_length=10,  blank=True, null=True)
    matric_description        = models.TextField(blank=True, null=True)

    # ── INTER DOCUMENTS (11 & 12) ─────────────────────────────────────
    inter_degree_front        = models.FileField(upload_to='study_cms/inter/', null=True, blank=True)
    inter_degree_back         = models.FileField(upload_to='study_cms/inter/', null=True, blank=True)
    inter_result_card_front   = models.FileField(upload_to='study_cms/inter/', null=True, blank=True)
    inter_result_card_back    = models.FileField(upload_to='study_cms/inter/', null=True, blank=True)
    inter_institute           = models.CharField(max_length=255, blank=True, null=True)
    inter_year                = models.CharField(max_length=10,  blank=True, null=True)
    inter_description         = models.TextField(blank=True, null=True)

    # ── HIGHER EDUCATION — BS ─────────────────────────────────────────
    bs_degree_front           = models.FileField(upload_to='study_cms/bs/', null=True, blank=True)
    bs_degree_back            = models.FileField(upload_to='study_cms/bs/', null=True, blank=True)
    bs_transcript_front       = models.FileField(upload_to='study_cms/bs/', null=True, blank=True)
    bs_transcript_back        = models.FileField(upload_to='study_cms/bs/', null=True, blank=True)
    bs_institute              = models.CharField(max_length=255, blank=True, null=True)
    bs_year                   = models.CharField(max_length=10,  blank=True, null=True)
    bs_description            = models.TextField(blank=True, null=True)

    # ── HIGHER EDUCATION — MS ─────────────────────────────────────────
    ms_degree_front           = models.FileField(upload_to='study_cms/ms/', null=True, blank=True)
    ms_degree_back            = models.FileField(upload_to='study_cms/ms/', null=True, blank=True)
    ms_transcript_front       = models.FileField(upload_to='study_cms/ms/', null=True, blank=True)
    ms_transcript_back        = models.FileField(upload_to='study_cms/ms/', null=True, blank=True)
    ms_institute              = models.CharField(max_length=255, blank=True, null=True)
    ms_year                   = models.CharField(max_length=10,  blank=True, null=True)
    ms_description            = models.TextField(blank=True, null=True)

    # ── PROFESSIONAL DOCUMENTS ────────────────────────────────────────
    cv                        = models.FileField(upload_to='study_cms/professional/', null=True, blank=True)
    ielts_pte                 = models.FileField(upload_to='study_cms/professional/', null=True, blank=True)
    ielts_pte_year            = models.CharField(max_length=10,  blank=True, null=True)
    ielts_pte_description     = models.TextField(blank=True, null=True)

    # ── System Fields ─────────────────────────────────────────────────
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Documents — {self.student.name}"


class ExperienceLetter(models.Model):
    """Multiple experience letters per student"""
    student         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='experience_letters')
    uploaded_by     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_experience_letters')
    file            = models.FileField(upload_to='study_cms/professional/')
    organization    = models.CharField(max_length=255, blank=True, null=True)
    year            = models.CharField(max_length=10,  blank=True, null=True)
    description     = models.TextField(blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Experience Letter — {self.student.name}"


class ReferenceLetter(models.Model):
    """Multiple reference letters per student"""
    student         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reference_letters')
    uploaded_by     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_reference_letters')
    file            = models.FileField(upload_to='study_cms/professional/')
    referee_name    = models.CharField(max_length=255, blank=True, null=True)
    year            = models.CharField(max_length=10,  blank=True, null=True)
    description     = models.TextField(blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reference Letter — {self.student.name}"


class OtherDocument(models.Model):
    """Any other documents — training certs, etc."""
    student         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='other_documents')
    uploaded_by     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_other_documents')
    file            = models.FileField(upload_to='study_cms/other/')
    document_name   = models.CharField(max_length=255, blank=True, null=True)
    year            = models.CharField(max_length=10,  blank=True, null=True)
    description     = models.TextField(blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Other Document — {self.student.name}"