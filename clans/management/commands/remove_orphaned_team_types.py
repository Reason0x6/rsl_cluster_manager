from django.core.management.base import BaseCommand
from clans.models import TeamType

class Command(BaseCommand):
    help = 'Removes orphaned team types from all players'

    def handle(self, *args, **kwargs):
        TeamType.remove_orphaned_from_players()
        self.stdout.write(self.style.SUCCESS('Successfully removed orphaned team types from players'))
