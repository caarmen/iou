import logging
import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create default admin user if it does not exist"

    def handle(self, *args, **options):
        create_admin_user_if_needed()


def create_admin_user_if_needed():
    """
    Create an admin user with the default password, if the admin user doesn't already exist.
    """
    admin_username = os.getenv("ADMIN_USER", "admin")
    password = "defaultpassword"
    try:
        User.objects.get(username=admin_username)
    except User.DoesNotExist:
        User.objects.create_superuser(
            username=admin_username,
            password=password,
        )
        logger.warning(
            f"\x1b[31;1mCreated superuser {admin_username} with password {password}. Change this password immediately!\x1b[0m"
        )
