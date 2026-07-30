import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Automatically creates a superuser for Neon PostgreSQL environment.'

    def handle(self, *args, **options):
        User = get_user_model()
        
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'OnurAdmin123!')

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, password=password)
            self.stdout.write(self.style.SUCCESS(f'✅ Superuser "{username}" successfully created!'))
        else:
            self.stdout.write(self.style.WARNING(f'ℹ️ Superuser "{username}" already exists.'))