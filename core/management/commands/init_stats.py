from django.core.management.base import BaseCommand
from core.models import SiteStats

class Command(BaseCommand):
    help = 'Initialize SiteStats if not exists'

    def handle(self, *args, **options):
        SiteStats.objects.get_or_create(pk=1, defaults={'total_views': 0})
        self.stdout.write(self.style.SUCCESS('SiteStats initialized successfully!'))