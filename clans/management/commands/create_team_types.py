from django.core.management.base import BaseCommand
from clans.models import TeamType

class Command(BaseCommand):
    help = 'Creates initial team types'

    def handle(self, *args, **kwargs):
        for code, name in TeamType.TEAM_CHOICES:
            TeamType.objects.get_or_create(name=code)
        self.stdout.write(self.style.SUCCESS('Successfully created team types'))