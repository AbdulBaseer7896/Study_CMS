# myapp/Models/Auth_models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from myapp.Utils.storage_utils import get_storage



class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        CONSULTANT = 'consultant', 'Consultant'
        STUDENT = 'student', 'Student'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT
    )

    # Personal Information
    name = models.CharField(max_length=150)
    father_name = models.CharField(max_length=150, blank=True, null=True)
    cnic = models.CharField(max_length=15, unique=True, blank=True, null=True)
    dob = models.DateField()
    address = models.TextField(blank=True, null=True)
    highest_education = models.CharField(max_length=150, blank=True, null=True)

    # Contact Information
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    father_phone = models.CharField(max_length=20, blank=True, null=True)

    # ─── Student-only fields ───────────────────────────────────────────
    # Which consultant referred/brought this student
    reference = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referred_students',
        limit_choices_to={'role': 'consultant'},   # only consultants allowed
        help_text="Consultant who referred this student"
    )

    # Which consultant is currently managing/assigned to this student
    assigned_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_students',
        limit_choices_to={'role': 'consultant'},   # only consultants allowed
        help_text="Consultant currently assigned to this student"
    )
    # ──────────────────────────────────────────────────────────────────

    profile_picture = models.ImageField(
        upload_to='study_cms/profile_pics/',
        storage=get_storage,   # ← calls utility, switches with STORAGE_BACKEND
        null=True,
        blank=True
    )


    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['email', 'phone', 'name', 'dob']

    def __str__(self):
        return f"{self.name} ({self.role})"