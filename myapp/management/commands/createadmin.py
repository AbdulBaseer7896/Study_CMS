from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    help = "Create admin user if not exists"

    def handle(self, *args, **kwargs):
        username = os.getenv("DJANGO_ADMIN_USERNAME", "admin")
        email = os.getenv("DJANGO_ADMIN_EMAIL", "admin@gmail.com")
        password = os.getenv("DJANGO_ADMIN_PASSWORD", "pass1234")

        # Default DOB to Jan 1, 2000
        dob = date(2000, 1, 1)

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                dob=dob,  # Add this
            )
            self.stdout.write(self.style.SUCCESS("Admin user created"))
        else:
            self.stdout.write("Admin user already exists")