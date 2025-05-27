from django import forms
from .models import Player, Clan, CvC, Siege, HydraClash, ChimeraClash, TeamType
import json

class PlayerForm(forms.ModelForm):
    team_types = forms.ModelMultipleChoiceField(
        queryset=TeamType.objects.all(),
        widget=forms.CheckboxSelectMultiple(),  # Remove the sr-only class
        required=False,
    )

    class Meta:
        model = Player
        fields = ['name', 'player_id_ingame', 'level', 'player_power', 'discord_id', 'team_types']

class ClanForm(forms.ModelForm):
    clan_boss_level = forms.MultipleChoiceField(
        choices=Clan.CLAN_BOSS_LEVELS,
        widget=forms.CheckboxSelectMultiple(
            attrs={'class': 'sr-only'}
        )
    )

    class Meta:
        model = Clan
        fields = ['name', 'clan_level', 'personal_rewards_cvc_threshold',
            'non_pr_cvc_threshold', 'clan_boss_level', 'hydra_clash_required_score','chimera_clash_required_score', 'players']

    def clean_clan_boss_level(self):
        levels = self.cleaned_data['clan_boss_level']
        json_levels = json.dumps(list(levels))  # Convert to list and then to JSON
        print(f"Saving clan boss levels: {json_levels}")  # Debug print
        return json_levels

class CvCForm(forms.ModelForm):
    class Meta:
        model = CvC
        exclude = ['clan'] # Clan will be set in the view

class SiegeForm(forms.ModelForm):
    class Meta:
        model = Siege
        fields = ['position', 'points', 'date_recorded']
        widgets = {
            'date_recorded': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class HydraClashForm(forms.ModelForm):
    opponent_scores = forms.JSONField(widget=forms.HiddenInput())
    
    class Meta:
        model = HydraClash
        fields = ['date_recorded', 'opponent_scores']
        widgets = {
            'date_recorded': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ChimeraClashForm(forms.ModelForm):
    opponent_scores = forms.JSONField(widget=forms.HiddenInput())
    
    class Meta:
        model = ChimeraClash
        fields = ['date_recorded', 'opponent_scores']
        widgets = {
            'date_recorded': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }