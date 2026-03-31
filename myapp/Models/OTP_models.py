# myapp/Models/OTP_models.py
import random
from django.db import models
from django.utils import timezone
from datetime import timedelta


class PasswordResetOTP(models.Model):
    """Stores a 6-digit OTP for password reset. Expires after 40 seconds."""

    user       = models.ForeignKey('myapp.User', on_delete=models.CASCADE, related_name='otps')
    otp        = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used    = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def is_valid(self):
        """Returns True if OTP is within 40 seconds and not used."""
        expiry = self.created_at + timedelta(seconds=40)
        return not self.is_used and timezone.now() < expiry

    @classmethod
    def generate_for_user(cls, user):
        """Delete old OTPs for user, create a fresh one."""
        cls.objects.filter(user=user).delete()
        otp_code = str(random.randint(100000, 999999))
        return cls.objects.create(user=user, otp=otp_code)

    def __str__(self):
        return f"OTP for {self.user.email} — {'valid' if self.is_valid() else 'expired'}"
