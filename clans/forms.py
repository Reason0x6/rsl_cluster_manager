from django import forms
from django.shortcuts import render, get_object_or_404
from .models import Player, Clan, CvC, Siege, HydraClash, ChimeraClash, TeamType, SiegePlan, PostAssignment
import json

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
        print(f"Saving clan boss levels: {json_levels}")  # Debug print
        return json_levels

class CvCForm(forms.ModelForm):
    class Meta:
        model = CvC
        exclude = ['clan'] # Clan will be set in the view

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

        for post in posts:
            post_number = post['Post']
            choices = post['Choices']

            # Team Choice Dropdown
            self.fields[f'post_{post_number}_team_choice'] = forms.ChoiceField(
                choices=[('', 'Select a team type')] + [(choice, choice.replace('_', ' ').title()) for choice in choices],
                required=True,
                initial=initial_data.get(post_number, {}).get('team_choice'),
                widget=forms.Select(attrs={
                    'class': 'bg-gray-700 text-white rounded-lg team-choice',
                    'data-post-number': post_number,  # Add a data attribute for JavaScript
                })
            )

            # Player Dropdown
            self.fields[f'post_{post_number}_player'] = forms.ChoiceField(
                choices=[],  # Empty choices; will be populated by JavaScript
                required=False,
                initial=initial_data.get(post_number, {}).get('player'),
                widget=forms.Select(attrs={
                    'class': 'bg-gray-700 text-white rounded-lg player-dropdown',
                    'data-post-number': post_number,
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

def assign_siege_plan(request, plan_id):
    siege_plan = get_object_or_404(SiegePlan, id=plan_id)
    clan = siege_plan.clan
    posts = siege_plan.plan_data

    # Get all players and their team types
    players = Player.objects.filter(clan=clan).prefetch_related('team_types')
    player_data = [
        {
            'id': str(player.uuid),
            'name': player.name,
            'team_types': [team.name for team in player.team_types.all()]
        }
        for player in players
    ]

    # Retrieve saved assignments
    saved_assignments = {
        assignment.post_number: {
            'team_choice': assignment.team_choice,
            'player': assignment.assigned_player.uuid if assignment.assigned_player else None
        }
        for assignment in PostAssignment.objects.filter(siege_plan=siege_plan)
    }

    if request.method == 'POST':
        form = PostAssignmentForm(request.POST, clan=clan, posts=posts)
        if form.is_valid():
            # Save assignments
            for post in posts:
                
                post_number = post['Post']
                team_choice = form.cleaned_data[f'post_{post_number}_team_choice']
                player_uuid = form.cleaned_data[f'post_{post_number}_player']
                
                player = Player.objects.get(uuid=player_uuid) if player_uuid else None
                assignment, created = PostAssignment.objects.get_or_create(
                    siege_plan=siege_plan,
                    post_number=post_number,
                )
                assignment.team_choice = team_choice
                assignment.assigned_player = player
                assignment.save()

            return redirect('clan_detail', clan_id=clan.clan_id)
    else:
        form = PostAssignmentForm(clan=clan, posts=posts, initial=saved_assignments)

    return render(request, 'clans/assign_siege_plan.html', {
        'form': form,
        'siege_plan': siege_plan,
        'player_data': json.dumps(player_data),  # Serialize player data as JSON
    })