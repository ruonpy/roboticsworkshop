from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from showcase.utils import check_and_grant_badges


class Command(BaseCommand):
    help = "Checks and grants missing badges for all users."

    def handle(self, *args, **options):
        users = User.objects.all()

        checked = 0

        for user in users:
            check_and_grant_badges(user)
            checked += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Badge synchronization completed. {checked} users checked."
            )
        )