import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

# CREATE SUPERUSER COMMAND

class Command(BaseCommand):
    help = 'Automatically creates a superuser for Neon PostgreSQL environment.'

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not username:
            raise CommandError(
                'DJANGO_SUPERUSER_USERNAME environment variable is not set.'
            )

        if not password:
            raise CommandError(
                'DJANGO_SUPERUSER_PASSWORD environment variable is not set.'
            )

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'Superuser "{username}" already exists.'
                )
            )
            return

        User.objects.create_superuser(
            username=username,
            password=password
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Superuser "{username}" successfully created!'
            )
        )