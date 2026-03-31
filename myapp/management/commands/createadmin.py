
# myapp/management/commands/createadmin.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date
import os

User = get_user_model()


class Command(BaseCommand):
    help = "Creates a default admin user if not exists"

    def handle(self, *args, **kwargs):
        # You can set these via environment variables in Render, or fallback to defaults
        username = os.getenv("DJANGO_ADMIN_USERNAME", "admin")
        email = os.getenv("DJANGO_ADMIN_EMAIL", "admin@gmail.com")
        password = os.getenv("DJANGO_ADMIN_PASSWORD", "pass1234")
        name = os.getenv("DJANGO_ADMIN_NAME", "Administrator")
        phone = os.getenv("DJANGO_ADMIN_PHONE", "0000000000")
        dob = os.getenv("DJANGO_ADMIN_DOB", "2000-01-01")  # YYYY-MM-DD format
        dob = date.fromisoformat(dob)

        # Check if admin already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING("Admin user already exists. Skipping creation."))
            return

        # Create superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            name=name,
            phone=phone,
            dob=dob,
            role=User.Role.ADMIN
        )

        self.stdout.write(self.style.SUCCESS(f"Admin user '{username}' created successfully!"))