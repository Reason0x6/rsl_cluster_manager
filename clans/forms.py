import logging
from django import forms
from django.shortcuts import render, get_object_or_404
from .models import Player, Clan, CvC, Siege, HydraClash, ChimeraClash, TeamType, SiegePlan, PostAssignment
import json
import logging
logger = logging.getLogger(__name__)

class PlayerForm(forms.ModelForm):
    team_types = forms.ModelMultipleChoiceField(
        queryset=TeamType.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )

    class Meta:
        model = Player
        fields = ['name', 'player_id_ingame', 'hh_optimiser_link', 'level', 'player_power', 'discord_id', 'team_types']

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
        return json_levels

class CvCForm(forms.ModelForm):
    class Meta:
        model = CvC
        exclude = ['clan']

class SiegeForm(forms.ModelForm):
    class Meta:
        model = Siege
        fields = ['position', 'points', 'opponent_clan', 'opponent_score', 'date_recorded']
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

class SiegePlanForm(forms.ModelForm):
    class Meta:
        model = SiegePlan
        fields = ['name', 'plan_data']
        widgets = {
            'plan_data': forms.Textarea(attrs={
                'class': 'bg-gray-700 text-white rounded-lg p-4',
                'placeholder': 'Enter JSON data here...',
                'rows': 10,
            }),
        }

class PostAssignmentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        clan = kwargs.pop('clan')
        posts = kwargs.pop('posts')
        initial_data = kwargs.pop('initial', {})
        super().__init__(*args, **kwargs)
        clanObj = Clan.objects.get(name=clan)
        # Get all players in the clan
        players = clanObj.players.all()
        player_choices = [(str(player.uuid), player.name) for player in players]      
        logger.debug(f"{player_choices}")
        for post in posts:
            post_number = post['Post']
            choices = post['Choices']

            # Team Choice Dropdown
            self.fields[f'post_{post_number}_team_choice'] = forms.ChoiceField(
                choices=[('', 'Select a team type')] + [(choice, choice.replace('_', ' ').title()) for choice in choices],
                required=False,
                initial=initial_data.get(post_number, {}).get('team_choice'),  # Prepopulate with saved value
                widget=forms.Select(attrs={
                    'class': 'bg-gray-700 text-white rounded-lg team-choice',
                    'data-post-number': post_number,
                })
            )
            # Player Dropdown
            self.fields[f'post_{post_number}_player'] = forms.ChoiceField(
                choices=player_choices,  # Populate with all players in the clan
                required=False,
                initial=initial_data.get(post_number, {}).get('player'),  # Prepopulate with saved value
                widget=forms.Select(attrs={
                    'class': 'bg-gray-700 text-white rounded-lg player-dropdown',
                    'data-post-number': post_number,
                    'data-selected-player': initial_data.get(post_number, {}).get('player'),  # Add data-selected-player attribute
    
                })
            )

    def add_player_team_types(self):
        """
        Add data-team-types attributes to player options in the dropdown.
        """
        for field_name, field in self.fields.items():
            if field_name.endswith('_player'):
                for option in field.widget.choices.queryset:
                    team_types = ','.join([team.name for team in option.team_types.all()])
                    field.widget.attrs[f'data-team-types-{option.pk}'] = team_types
