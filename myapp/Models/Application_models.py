# myapp/Models/Application_models.py
from django.db import models
from myapp.Models.Auth_models import User


class Application(models.Model):

    class Status(models.TextChoices):
        DRAFT           = 'draft',          'Draft'
        APPLIED         = 'applied',        'Applied'
        UNDER_REVIEW    = 'under_review',   'Under Review'
        OFFER_RECEIVED  = 'offer_received', 'Offer Received'
        ACCEPTED        = 'accepted',       'Accepted'
        REJECTED        = 'rejected',       'Rejected'
        WITHDRAWN       = 'withdrawn',      'Withdrawn'
        ENROLLED        = 'enrolled',       'Enrolled'

    # ── Core Relations ────────────────────────────────────────────────
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applications',
        limit_choices_to={'role': 'student'}
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_applications'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_applications'
    )

    # ── University Info ───────────────────────────────────────────────
    application_name        = models.CharField(max_length=255)
    country                 = models.CharField(max_length=100)
    university              = models.CharField(max_length=255)
    city                    = models.CharField(max_length=100)
    university_portal_link  = models.URLField(blank=True, null=True)
    portal_login_id         = models.CharField(max_length=255, blank=True, null=True)
    portal_login_password   = models.CharField(max_length=255, blank=True, null=True)

    # ── Course Info ───────────────────────────────────────────────────
    degree_name             = models.CharField(max_length=255)
    course_title            = models.CharField(max_length=255)

    # ── Fee Info ──────────────────────────────────────────────────────
    apply_fee               = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    yearly_fee              = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # ── Important Dates ───────────────────────────────────────────────
    last_date_to_apply      = models.DateField(blank=True, null=True)
    last_date_fee_submit    = models.DateField(blank=True, null=True)
    expected_offer_date     = models.DateField(blank=True, null=True)

    # ── Status & Documents ────────────────────────────────────────────
    status                  = models.CharField(
                                max_length=20,
                                choices=Status.choices,
                                default=Status.DRAFT
                             )
    offer_letter            = models.FileField(
                                upload_to='study_cms/applications/offer_letters/',
                                blank=True, null=True
                             )
    fee_slip                = models.FileField(
                                upload_to='study_cms/applications/fee_slips/',
                                blank=True, null=True
                             )

    # ── System Fields ─────────────────────────────────────────────────
    created_at              = models.DateTimeField(auto_now_add=True)
    updated_at              = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.name} → {self.university} ({self.status})"


class ApplicationModule(models.Model):
    """Main modules/subjects of the course — multiple per application"""
    application     = models.ForeignKey(
                        Application,
                        on_delete=models.CASCADE,
                        related_name='modules'
                      )
    module_name     = models.CharField(max_length=255)
    description     = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.application.course_title} — {self.module_name}"


class ApplicationImage(models.Model):
    """Extra images/files — multiple per application"""
    application     = models.ForeignKey(
                        Application,
                        on_delete=models.CASCADE,
                        related_name='extra_images'
                      )
    uploaded_by     = models.ForeignKey(
                        User,
                        on_delete=models.SET_NULL,
                        null=True
                      )
    image           = models.FileField(upload_to='study_cms/applications/extra/')
    caption         = models.CharField(max_length=255, blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image — {self.application.application_name}"