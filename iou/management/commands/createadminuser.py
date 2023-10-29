# This was generated by ChatGPT

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create default admin user if it does not exist"

    def handle(self, *args, **options):
        username = "admin"
        password = "defaultpassword"

        if not User.objects.filter(username=username).exists():
            admin = User.objects.create_user(username, password=password)
            admin.is_superuser = True
            admin.is_staff = True
            admin.save()
            self.stdout.write(self.style.SUCCESS("Default admin user created."))
        else:
            self.stdout.write(self.style.WARNING("Default admin user already exists."))
