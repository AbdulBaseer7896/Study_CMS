# myapp/Models/Document_models.py  (added upload_time tracking per field)
from django.db import models
from django.utils import timezone
from myapp.Models.Auth_models import User


class StudentDocument(models.Model):
    """Single model for ALL student documents — grouped by category"""

    student = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='documents', limit_choices_to={'role': 'student'}
    )
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents'
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

    # ── Per-field upload timestamps (for 15-min student edit window) ──
    field_upload_times        = models.JSONField(default=dict, blank=True)
    # e.g. {"cnic_front": "2025-01-01T10:00:00Z", ...}

    # ── System Fields ─────────────────────────────────────────────────
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def record_upload_time(self, field_name):
        """Call after saving a new file to stamp the upload time."""
        self.field_upload_times[field_name] = timezone.now().isoformat()
        self.save(update_fields=['field_upload_times'])

    def student_can_edit_field(self, field_name):
        """Students may replace/delete within 15 min of first upload."""
        ts = self.field_upload_times.get(field_name)
        if not ts:
            return True  # never uploaded → can upload
        from datetime import datetime, timezone as dt_tz
        upload_time = datetime.fromisoformat(ts)
        if upload_time.tzinfo is None:
            upload_time = upload_time.replace(tzinfo=dt_tz.utc)
        window_end = upload_time + timezone.timedelta(minutes=15)
        return timezone.now() < window_end

    def __str__(self):
        return f"Documents of {self.student.name}"


class ExperienceLetter(models.Model):
    student     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='experience_letters',
                                    limit_choices_to={'role': 'student'})
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_experience_letters')
    file        = models.FileField(upload_to='study_cms/experience/')
    title       = models.CharField(max_length=255, blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def student_can_edit(self):
        window_end = self.created_at + timezone.timedelta(minutes=15)
        return timezone.now() < window_end

    def __str__(self):
        return f"Experience Letter — {self.student.name}"


class ReferenceLetter(models.Model):
    student     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reference_letters',
                                    limit_choices_to={'role': 'student'})
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_reference_letters')
    file        = models.FileField(upload_to='study_cms/reference/')
    title       = models.CharField(max_length=255, blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def student_can_edit(self):
        window_end = self.created_at + timezone.timedelta(minutes=15)
        return timezone.now() < window_end

    def __str__(self):
        return f"Reference Letter — {self.student.name}"


class OtherDocument(models.Model):
    student     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='other_documents',
                                    limit_choices_to={'role': 'student'})
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_other_documents')
    file        = models.FileField(upload_to='study_cms/other/')
    title       = models.CharField(max_length=255, blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def student_can_edit(self):
        window_end = self.created_at + timezone.timedelta(minutes=15)
        return timezone.now() < window_end

    def __str__(self):
        return f"Other Document — {self.student.name}"
