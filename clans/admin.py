from django.contrib import admin
from .models import Clan, Player, CvC, HydraClash, ChimeraClash, Siege, TeamType

@admin.register(Siege)
class SiegeAdmin(admin.ModelAdmin):
    list_display = ('clan', 'position', 'points', 'date_recorded')
    list_filter = ('clan', 'date_recorded')
    search_fields = ('clan__name',)
    date_hierarchy = 'date_recorded'
    ordering = ('-date_recorded',)

@admin.register(CvC)
class CvCAdmin(admin.ModelAdmin):
    list_display = ('clan', 'opponent', 'tier', 'score', 'opponent_score', 'date_recorded')
    list_filter = ('clan', 'tier', 'date_recorded')
    search_fields = ('opponent',)

@admin.register(HydraClash)
class HydraClashAdmin(admin.ModelAdmin):
    list_display = ['clan', 'date_recorded', 'scores_display', 'delebrate_throw']
    list_filter = ['clan', 'delebrate_throw']
    ordering = ['-date_recorded']

@admin.register(ChimeraClash)
class ChimeraClashAdmin(admin.ModelAdmin):
    list_display = ['clan', 'date_recorded', 'scores_display']
    list_filter = ['clan']
    ordering = ['-date_recorded']

admin.site.register(Player)
admin.site.register(Clan)
admin.site.register(TeamType)
