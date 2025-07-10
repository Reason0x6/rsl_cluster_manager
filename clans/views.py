import base64
from decimal import Decimal
import logging
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from .models import TEAM_CHOICES, ArenaTeam, Clan, ClashScore, Player, TeamType, CvC, HydraClash, ChimeraClash, Siege, LABattle, SiegePlan, PostAssignment
from .forms import PlayerForm, ClanForm, CvCForm, SiegeForm, HydraClashForm, ChimeraClashForm, SiegePlanForm, PostAssignmentForm, ArenaTeamForm, PlayerManagementForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.conf import settings
import google.generativeai as genai
import jsonschema
import json
import os
import re
from django.db.models import Avg

logger = logging.getLogger(__name__)

def home(request):
    players = Player.objects.all().order_by('name')
    clans = Clan.objects.prefetch_related('players', 'cvcs', 'hydra_clashes', 'chimera_clashes', 'siege_records').all().order_by('name')

    # Prepare histories as lists for each clan (limit to latest 10 per type)
    for clan in clans:
        # Defensive: always use clan.players.all() for player count, not for history tables
        clan.cvc_history_list = [
            {'date': cvc.date_recorded.strftime('%Y-%m-%d'), 'score': cvc.score}
            for cvc in clan.cvcs.all().order_by('-date_recorded')[:10][::-1]
        ]
        # Defensive: fallback to empty list if no hydra clashes
        hydra_qs = clan.hydra_clashes.all().order_by('-date_recorded')[:10]
        clan.hydra_history_list = [
            {'date': hydra.date_recorded.strftime('%Y-%m-%d'), 'score': getattr(hydra, 'score', getattr(hydra, 'get', lambda: 0)())}
            for hydra in hydra_qs
        ] if hydra_qs else []
        chimera_qs = clan.chimera_clashes.all().order_by('-date_recorded')[:10]
        clan.chimera_history_list = [
            {'date': chimera.date_recorded.strftime('%Y-%m-%d'), 'score': getattr(chimera, 'score', getattr(chimera, 'get', lambda: 0)())}
            for chimera in chimera_qs
        ] if chimera_qs else []
        siege_qs = clan.siege_records.all().order_by('-date_recorded')[:10]
        clan.siege_history_list = [
            {'date': siege.date_recorded.strftime('%Y-%m-%d'), 'points': siege.points}
            for siege in siege_qs
        ] if siege_qs else []

    context = {
        'players': players,
        'clans': clans,
    }
    return render(request, 'clans/home.html', context)

@login_required
def player_detail(request, uuid):  # Change from player_uuid to uuid
    player = get_object_or_404(Player, uuid=uuid)
    arena_teams = ArenaTeam.objects.filter(player=player)
    logger.info(f"{arena_teams}")
            
    clash_scores_data = {
        "labels": [
            f"{score.type} ({score.date_recorded.strftime('%Y-%m-%d')})"
            for score in player.clash_scores.all()
        ],
        "hydra_scores": [float(score.score) for score in player.clash_scores.filter(type="hydra")],
        "chimera_scores": [float(score.score) for score in player.clash_scores.filter(type="chimera")],
    }

    context = {
        "player": player,
        "clash_scores": player.clash_scores.all().order_by("-date_recorded"),
        "arena_teams": arena_teams,
        "all_team_types": TeamType.objects.all().order_by("name"),
        "clash_scores_data": json.dumps(clash_scores_data),
    }
    return render(request, 'clans/player_detail.html', context)

@login_required
def player_edit(request, uuid):  # Changed from player_uuid to uuid
    player = get_object_or_404(Player, uuid=uuid)
    if request.method == 'POST':
        form = PlayerForm(request.POST, instance=player)
        if form.is_valid():
            form.save()
            return redirect('player_detail', uuid=player.uuid)  # Changed parameter name here too
    else:
        form = PlayerForm(instance=player)
    
    return render(request, 'clans/player_form.html', {
        'form': form,
        'player': player,
        'action': 'Edit'
    })

@login_required
def player_create(request):
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            player = form.save()
            return redirect('player_detail', uuid=player.uuid)  # Changed from player_uuid to uuid
    else:
        form = PlayerForm()
    context = {'form': form, 'action': 'Create'}
    return render(request, 'clans/player_form.html', context)

@login_required
def clan_detail(request, clan_id):
    clan = get_object_or_404(Clan, clan_id=clan_id)

    # Defensive: ensure we are not accidentally passing the wrong object to a decorator or function
    # Calculate CvC Performance (wins vs total)
    activities_config = get_activities_config(clan)
    cvc_records = [
        record for record in activities_config['CvC']['records']
    ]
    won_records = [
        record for record in cvc_records if record.score > record.opponent_score
    ]

    if cvc_records:
        cvc_performance = (len(won_records) / len(cvc_records)) * 100
    else:
        cvc_performance = Decimal('0')

    # Calculate Siege Performance (position 1 = win)
    siege_records = clan.siege_records.all()
    if siege_records.exists():
        siege_wins = siege_records.filter(position=1).count()
        siege_performance = Decimal(str(siege_wins)) / Decimal(str(siege_records.count())) * 100
    else:
        siege_performance = Decimal('0')

    # Calculate Hydra Progress
    hydra_clashes = clan.hydra_clashes.all()
    if hydra_clashes.exists():
        total_positions = sum(clash.rank for clash in hydra_clashes)
        avg_position = Decimal(str(total_positions)) / Decimal(str(hydra_clashes.count()))
        hydra_progress = max(Decimal('0'), Decimal('100') * (Decimal('5') - avg_position) / Decimal('4'))
    else:
        hydra_progress = Decimal('0')

    # Calculate Chimera Progress
    chimera_clashes = clan.chimera_clashes.all()
    if chimera_clashes.exists():
        total_positions = sum(clash.rank for clash in chimera_clashes)
        avg_position = Decimal(str(total_positions)) / Decimal(str(chimera_clashes.count()))
        chimera_progress = max(Decimal('0'), Decimal('100') * (Decimal('5') - avg_position) / Decimal('4'))
    else:
        chimera_progress = Decimal('0')

    hydra_scores = [clash.get_clan_score() for clash in clan.hydra_clashes.all()]
    hydra_avg = sum(hydra_scores) / len(hydra_scores) if hydra_scores else None
    chimera_scores = [clash.get_clan_score() for clash in clan.chimera_clashes.all()]
    chimera_avg = sum(chimera_scores) / len(chimera_scores) if chimera_scores else None
    context = {
        'clan': clan,
        'activities_config': activities_config,
        'cvc_performance': round(float(cvc_performance), 1),
        'hydra_progress': round(float(hydra_progress), 1),
        'chimera_progress': round(float(chimera_progress), 1),
        'siege_performance': round(float(siege_performance), 1),
        'hydra_avg': hydra_avg,
        'chimera_avg': chimera_avg,
    }
    return render(request, 'clans/clan_detail.html', context)

@login_required
def clan_edit(request, clan_id):
    clan = get_object_or_404(Clan, clan_id=clan_id)
    if request.method == 'POST':
        form = ClanForm(request.POST, instance=clan)
        if form.is_valid():
            clan = form.save()
            selected_players = form.cleaned_data.get('players', [])
            selected_player_ids = [p.pk for p in selected_players]
            # Set selected players' .clan and ensure they are only in this clan's players m2m
            for player in selected_players:
                if player.clan != clan:
                    player.clan = clan
                    player.save(update_fields=['clan'])
                # Remove player from all other clans' players m2m except this one
                from .models import Clan as ClanModel
                other_clans = ClanModel.objects.filter(players=player).exclude(pk=clan.pk)
                for c in other_clans:
                    c.players.remove(player)
            # Remove players not selected from this clan and clear their .clan if needed
            for player in clan.players.exclude(pk__in=selected_player_ids):
                player.clan = None
                player.save(update_fields=['clan'])
                clan.players.remove(player)
            return redirect('clan_detail', clan_id=clan.clan_id)
    else:
        form = ClanForm(instance=clan)
    context = {'form': form, 'clan': clan, 'action': 'Edit'}
    return render(request, 'clans/clan_form.html', context)

@login_required
def clan_create(request):
    if request.method == 'POST':
        form = ClanForm(request.POST)
        if form.is_valid():
            clan = form.save()
            return redirect('clan_detail', clan_id=clan.clan_id)
    else:
        form = ClanForm()
    context = {'form': form, 'action': 'Create'}
    return render(request, 'clans/clan_form.html', context)

# --- Create Views for Activities ---

@login_required
def cvc_create(request, clan_id):
    clan = get_object_or_404(Clan, clan_id=clan_id)
    if request.method == 'POST':
        form = CvCForm(request.POST)
        if form.is_valid():
            cvc = form.save(commit=False)
            cvc.clan = clan
            cvc.save()
            return redirect('clan_detail', clan_id=clan.clan_id)
    else:
        form = CvCForm()
    context = {
        'form': form,
        'clan': clan,
        'activity_type': 'CvC Record',
        'action_verb': 'Add'
    }
    return render(request, 'clans/generic_activity_form.html', context)

@login_required
def hydra_clash_create(request, clan_id):
    clan = get_object_or_404(Clan, clan_id=clan_id)
    if request.method == 'POST':
        form = HydraClashForm(request.POST)
        if form.is_valid():
            hydra_clash = form.save(commit=False)
            hydra_clash.clan = clan
            hydra_clash.save()
            return redirect('clan_detail', clan_id=clan.clan_id)
    else:
        form = HydraClashForm()
    context = {
        'form': form,
        'clan': clan,
        'activity_type': 'Hydra Clash Record',
        'action_verb': 'Add'
    }
    return render(request, 'clans/generic_activity_form.html', context)

@login_required
def chimera_clash_create(request, clan_id):
    clan = get_object_or_404(Clan, clan_id=clan_id)
    if request.method == 'POST':
        form = ChimeraClashForm(request.POST)
        if form.is_valid():
            chimera_clash = form.save(commit=False)
            chimera_clash.clan = clan
            chimera_clash.save()
            return redirect('clan_detail', clan_id=clan.clan_id)
    else:
        form = ChimeraClashForm()
    context = {
        'form': form,
        'clan': clan,
        'activity_type': 'Chimera Clash Record',
        'action_verb': 'Add'
    }
    return render(request, 'clans/generic_activity_form.html', context)

@login_required
def siege_create(request, clan_id):
    clan = get_object_or_404(Clan, clan_id=clan_id)
    if request.method == 'POST':
        form = SiegeForm(request.POST)
        if form.is_valid():
            siege = form.save(commit=False)
            siege.clan = clan
            siege.save()
            return redirect('clan_detail', clan_id=clan.clan_id)
    else:
        form = SiegeForm()
    
    context = {
        'form': form,
        'clan': clan,
        'action': 'Create',
        'title': 'Add Siege Record'
    }
    return render(request, 'clans/siege_form.html', context)

# --- Edit Views for Activities ---

@login_required
def cvc_edit(request, cvc_id):
    cvc_instance = get_object_or_404(CvC, cvc_id=cvc_id)
    clan = cvc_instance.clan
    if request.method == 'POST':
        form = CvCForm(request.POST, instance=cvc_instance)
        if form.is_valid():
            form.save()
            return redirect('clan_detail', clan_id=clan.clan_id)
    else:
        form = CvCForm(instance=cvc_instance)
    
    context = {
        'form': form,
        'clan': clan,
        'activity_instance': cvc_instance,
        'activity_type': 'CvC Record',
        'action_verb': 'Edit',
        'config': {
            'id_field': 'cvc_id',
            'color': 'green',
            'edit_url': 'cvc_edit',
            'create_url': 'cvc_create'
        }
    }
    return render(request, 'clans/generic_activity_form.html', context)

@login_required
def hydra_clash_edit(request, hydra_clash_id):
    hc_instance = get_object_or_404(HydraClash, hydra_clash_id=hydra_clash_id)
    clan = hc_instance.clan
    
    if request.method == 'POST':
        form = HydraClashForm(request.POST, instance=hc_instance)
        if form.is_valid():
            form.save()
            return redirect('clan_detail', clan_id=clan.clan_id)
    else:
        form = HydraClashForm(instance=hc_instance)
    
    context = {
        'form': form,
        'clan': clan,
        'activity_instance': hc_instance,
        'activity_type': 'Hydra Clash',
        'action_verb': 'Edit',
        'config': {
            'id_field': 'hydra_clash_id',
            'color': 'purple'
        }
    }
    return render(request, 'clans/generic_activity_form.html', context)

@login_required
def chimera_clash_edit(request, chimera_id):
    cc_instance = get_object_or_404(ChimeraClash, chimera_clash_id=chimera_id)
    clan = cc_instance.clan
    
    if request.method == 'POST':
        form = ChimeraClashForm(request.POST, instance=cc_instance)
        if form.is_valid():
            form.save()
            return redirect('clan_detail', clan_id=clan.clan_id)
    else:
        form = ChimeraClashForm(instance=cc_instance)
    
    context = {
        'form': form,
        'clan': clan,
        'activity_instance': cc_instance,
        'activity_type': 'Chimera Clash',
        'action_verb': 'Edit',
        'config': {
            'id_field': 'chimera_clash_id',
            'color': 'blue'
        }
    }
    return render(request, 'clans/generic_activity_form.html', context)

@login_required
def siege_edit(request, siege_id):
    siege = get_object_or_404(Siege, siege_id=siege_id)
    if request.method == 'POST':
        form = SiegeForm(request.POST, instance=siege)
        if form.is_valid():
            form.save()
            return redirect('clan_detail', clan_id=siege.clan.clan_id)
    else:
        form = SiegeForm(instance=siege)
    
    context = {
        'form': form,
        'siege': siege,
        'clan': siege.clan,
        'action': 'Edit',
        'title': 'Edit Siege Record'
    }
    return render(request, 'clans/siege_form.html', context)

@method_decorator([login_required, ensure_csrf_cookie], name='dispatch')
class PlayerListView(ListView):
    model = Player
    template_name = 'clans/player_list.html'
    context_object_name = 'players'

    def get_queryset(self):
        return Player.objects.all().prefetch_related('clans')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PlayerForm()
        return context

    def post(self, request, *args, **kwargs):
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('player_list')
        # If invalid, re-render the page with errors and current players
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

@method_decorator(login_required, name='dispatch')
class PlayerDetailView(DetailView):
    model = Player
    template_name = 'clans/player_detail.html'
    context_object_name = 'player'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_team_types'] = TeamType.objects.all()
        return context

@require_http_methods(["POST", "DELETE"])
@login_required
def manage_player_teams(request, player_uuid, team_id=None):
    try:
        player = Player.objects.get(uuid=player_uuid)
        
        if request.method == "POST":
            data = json.loads(request.body)
            team_types = TeamType.objects.filter(id__in=data.get('team_types', []))
            player.team_types.set(team_types)
            return JsonResponse({'status': 'success'})
            
        elif request.method == "DELETE" and team_id:
            player.team_types.remove(team_id)
            ArenaTeam.objects.filter(player=player).delete()
            return JsonResponse({'status': 'success'})
            
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_http_methods(["DELETE"])
@login_required
def delete_activity(request, activity_type, record_id):
    """API endpoint for deleting activity records"""
    try:
        # Map activity type to model
        model_map = {
            'cvc': CvC,
            'hydra': HydraClash,
            'chimera': ChimeraClash,
            'siege': Siege
        }
        
        # Get the appropriate model
        model = model_map.get(activity_type.lower())
        if not model:
            return JsonResponse({'error': 'Invalid activity type'}, status=400)
            
        # Get and delete the record
        record = get_object_or_404(model, pk=record_id)
        record.delete()
        
        return JsonResponse({'status': 'success'}, status=200)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["DELETE"])
@login_required
def delete_player(request, player_uuid):
    try:
        player = get_object_or_404(Player, uuid=player_uuid)
        player.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_activities_config(clan):
    """
    Returns configuration for clan activities including URLs and records
    """
    return {
        'CvC': {
            'title': 'Clan vs Clan',
            'icon': 'crossed-swords',
            'color': 'green',
            'threshold': clan.personal_rewards_cvc_threshold,
            'create_url': 'cvc_create',
            'edit_url': 'cvc_edit',
            'id_field': 'cvc_id',
            'records': clan.cvcs.all().order_by('-date_recorded')[:10]
        },
        'Hydra': {
            'title': 'Hydra Clan Boss',
            'icon': 'dragon-head',
            'color': 'purple',
            'threshold': clan.hydra_clash_required_score,
            'create_url': 'hydra_clash_create',
            'edit_url': 'hydra_clash_edit',
            'id_field': 'hydra_clash_id',
            'records': clan.hydra_clashes.all().order_by('-date_recorded')[:10]
        },
        'Chimera': {
            'title': 'Chimera Boss',
            'icon': 'beast-eye',
            'color': 'blue',
            'threshold': clan.chimera_clash_required_score,
            'create_url': 'chimera_clash_create',
            'edit_url': 'chimera_clash_edit',
            'id_field': 'chimera_clash_id',
            'records': clan.chimera_clashes.all().order_by('-date_recorded')[:10]
        },
        'Siege': {
            'title': 'Clan Siege',
            'icon': 'castle',
            'color': 'yellow',
            'threshold': None,
            'create_url': 'siege_create',
            'edit_url': 'siege_edit',
            'id_field': 'siege_id',
            'records': clan.siege_records.all().order_by('-date_recorded')[:10]
        }
    }

@require_http_methods(["POST"])
@login_required
def import_players(request):
    try:
        # Accept both string and already-parsed JSON
        if isinstance(request.body, bytes):
            body = request.body.decode('utf-8')
        else:
            body = request.body
        body = body.lstrip('\ufeff').strip()
        # Remove trailing commas before closing brackets/braces
        body = re.sub(r',(\s*[\]}])', r'\1', body)
        # Fix typo: "UMN" -> "UNM"
        body = body.replace('"UMN"', '"UNM"')
        # Defensive: ensure null is valid in JSON (should be, but just in case)
        body = body.replace("None", "null")
        # Try to parse JSON, provide a clear error if it fails
        try:
            data = json.loads(body)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid JSON: {str(e)}'
            }, status=400)

        imported_count = 0
        updated_count = 0

        for player_data in data:
            name = player_data.get('Name')
            if not name:
                continue

            player = Player.objects.filter(name__iexact=name).first()
            fields_map = {
                'player_power': player_data.get('Player Power'),
                'hydra_clash_score': player_data.get('Hydra Clash'),
                'hydra_difficulty_multi': player_data.get('Hydra Difficulty') or [],
                'chimera_clash_score': player_data.get('Chimera Clash'),
                'chimera_difficulty_multi': player_data.get('Chimera Difficulty') or [],
                'siege': player_data.get('Siege'),
                'activity': player_data.get('Activity'),
                'dependability': player_data.get('Dependability'),
                'development_notes': player_data.get('Development?'),
            }

            if player:
                for field, value in fields_map.items():
                    setattr(player, field, value)
                player.save()
                updated_count += 1
            else:
                Player.objects.create(
                    name=name,
                    **fields_map
                )
                imported_count += 1

        return JsonResponse({
            'status': 'success',
            'imported': imported_count,
            'updated': updated_count
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Import error: {str(e)}'
        }, status=400)

@login_required
def get_clan_players(request, clan_id):
    """API endpoint to get paginated players for a clan"""
    try:
        clan = get_object_or_404(Clan, clan_id=clan_id)
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 10))
        
        # Get players with pagination
        players = clan.players.all()[offset:offset+limit]
        
        # Convert player data to JSON-friendly format
        players_data = [{
            'uuid': str(player.uuid),
            'name': player.name,
            'player_power': float(player.player_power or 0),
        } for player in players]
        
        return JsonResponse({
            'status': 'success',
            'players': players_data,
            'total_count': clan.players.all().length
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def la_tracker(request):
    players = Player.objects.all().order_by('name')
    selected_player_id = request.GET.get('player')
    
    context = {
        'players': players,
        'selected_player': None,
        'battles': [],
    }
    
    if selected_player_id:
        selected_player = get_object_or_404(Player, uuid=selected_player_id)
        battles = selected_player.la_battles.all().order_by('date_recorded')[:30]  # Last 30 battles
        
        # Prepare chart data
        battle_dates = []
        total_points = []
        point_changes = []
        
        for battle in battles:
            battle_dates.append(battle.date_recorded.strftime('%Y-%m-%d %H:%M'))
            total_points.append(battle.current_points)
            point_changes.append(battle.points_change)
        
        context.update({
            'selected_player': selected_player,
            'battles': battles,
            'battle_dates': json.dumps(battle_dates),
            'total_points': json.dumps(total_points),
            'point_changes': json.dumps(point_changes)
        })
    
    return render(request, 'clans/la_tracker.html', context)

@require_http_methods(["POST"])
@login_required
def la_battle_create(request, player_id):
    try:
        player = get_object_or_404(Player, uuid=player_id)
        data = json.loads(request.body)
        
        # Create the battle
        battle = LABattle.objects.create(
            player=player,
            opponent_name=data['opponent_name'],
            points_change=data['points_change'],
            my_champions=data['my_champions'],
            opponent_champions=data['opponent_champions'],
            current_points=player.current_points + data['points_change']
        )
        
        # Update player's current points
        player.current_points = battle.current_points
        player.save()
        
        return JsonResponse({
            'status': 'success',
            'battle_id': str(battle.battle_id)
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_http_methods(["GET", "PUT", "DELETE"])
@login_required
def la_battle_detail(request, battle_id):
    battle = get_object_or_404(LABattle, battle_id=battle_id)
    
    if request.method == "GET":
        return JsonResponse({
            'battle_id': str(battle.battle_id),
            'opponent_name': battle.opponent_name,
            'points_change': battle.points_change,
            'my_champions': battle.my_champions,
            'opponent_champions': battle.opponent_champions,
            'current_points': battle.current_points,
            'date_recorded': battle.date_recorded.isoformat()
        })
    
    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
            points_diff = data['points_change'] - battle.points_change
            
            # Update battle
            battle.opponent_name = data['opponent_name']
            battle.points_change = data['points_change']
            battle.my_champions = data['my_champions']
            battle.opponent_champions = data['opponent_champions']
            battle.save()
            
            # Update player's points
            player = battle.player
            player.current_points += points_diff
            player.save()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    elif request.method == "DELETE":
        try:
            # Update player's points
            player = battle.player
            player.current_points -= battle.points_change
            player.save()
            
            battle.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)

@login_required
def create_siege_plan(request, clan_id):
    clan = get_object_or_404(Clan, clan_id=clan_id)
    if request.method == 'POST':
        form = SiegePlanForm(request.POST)
        if form.is_valid():
            siege_plan = form.save(commit=False)
            siege_plan.clan = clan
            siege_plan.save()
            return redirect('clan_detail', clan_id=clan.clan_id)
    else:
        form = SiegePlanForm()
    return render(request, 'clans/create_siege_plan.html', {'form': form, 'clan': clan})

@login_required
def assign_siege_plan(request, plan_id):
    siege_plan = get_object_or_404(SiegePlan, id=plan_id)
    clan = siege_plan.clan
    posts = siege_plan.plan_data

    clanObj = Clan.objects.get(name=clan)
    players = clanObj.players.all() 
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
            'team_choice': assignment.team_choice ,
            'player': str(assignment.assigned_player.uuid) if assignment.assigned_player else None
        }
        for assignment in PostAssignment.objects.filter(siege_plan=siege_plan)
    }

    if request.method == 'POST':
        form = PostAssignmentForm(request.POST, clan=clan, posts=posts)
        if form.is_valid():
            for post in posts:
                post_number = post['Post']
                team_choice = form.cleaned_data[f'post_{post_number}']
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
        'player_data': json.dumps(player_data), 
        'team_types': get_team_types_as_json(),  # Serialize list of tupples data as JSON
    })
@login_required
def export_siege_plan(request, plan_id):
    siege_plan = get_object_or_404(SiegePlan, id=plan_id)
    assignments = siege_plan.assignments.all()
    return render(request, 'clans/export_siege_plan.html', {'siege_plan': siege_plan, 'assignments': assignments})

@csrf_exempt
@login_required
def delete_siege_plan(request, plan_id):
    if request.method == 'DELETE':
        siege_plan = get_object_or_404(SiegePlan, id=plan_id)
        siege_plan.delete()
        return JsonResponse({'message': 'Siege plan deleted successfully.'}, status=200)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)



def get_team_types_as_json():
    """
    Retrieves all TeamType objects and returns them as a simple JSON array.
    """
    team_types_qs = TEAM_CHOICES  # Get both id and name fields


    # Use JsonResponse to serialize the list to JSON and return an HTTP response
    # The `safe=False` parameter is required to send a list as the top-level JSON object.
    return json.dumps(team_types_qs)

@login_required
def manage_arena_teams(request, player_uuid):
    player = get_object_or_404(Player, uuid=player_uuid)
    arena_teams = ArenaTeam.objects.filter(player=player)
    if request.method == 'POST':
        if 'add_team' in request.POST:
            form = ArenaTeamForm(request.POST)
            if form.is_valid():
                arena_team = form.save(commit=False)
                arena_team.player = player
                arena_team.save()
                logger.info(f"Managing arena teams for player: {arena_team})");
                return redirect('manage_arena_teams', player_uuid=player.uuid)
        elif 'remove_team' in request.POST:
            team_id = request.POST.get('team_id')
            ArenaTeam.objects.filter(id=team_id, player=player).delete()
            return redirect('manage_arena_teams', player_uuid=player.uuid)

    form = ArenaTeamForm(player=player)
    context = {
        'player': player,
        'arena_teams': arena_teams,
        'form': form,
    }
    return render(request, 'clans/player_teams.html', context)

@login_required
def manage_clans(request):
    clans = Clan.objects.all()
    selected_clan_id = request.GET.get('clan')
    selected_clan = get_object_or_404(Clan, pk=selected_clan_id) if selected_clan_id else clans.first()
    players = selected_clan.players.all() if selected_clan else Player.objects.none()

    context = {
        'clans': clans,
        'selected_clan': selected_clan,
        'players': players,
        'player_form': PlayerManagementForm(),
    }
    return render(request, 'clans/manage_clans.html', context)

# AJAX endpoint for saving player changes
@csrf_exempt
@login_required
def update_player_field(request, player_id):
    if request.method == 'POST':
        player = get_object_or_404(Player, pk=player_id)
        field = request.POST.get('field')
        value = request.POST.get('value')
        if field and hasattr(player, field):
            setattr(player, field, value)
            player.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@csrf_exempt
@login_required
def update_player_data(request, player_id):
    if request.method == 'POST':
        try:
            player = get_object_or_404(Player, pk=player_id)
            data = json.loads(request.body)

            updatable_fields = [
                'name', 'player_power', 'hydra_clash_score', 'hydra_difficulty_multi',
                'chimera_clash_score', 'chimera_difficulty_multi', 'siege', 'activity',
                'dependability', 'hh_optimiser_link', 'development_notes', 'clan'
            ]

            decimal_fields = ['player_power', 'hydra_clash_score', 'chimera_clash_score']

            old_clan = player.clan  # Track the old clan before update

            for field, value in data.items():
                if field not in updatable_fields:
                    continue
                if field in ['hydra_difficulty_multi', 'chimera_difficulty_multi']:
                    if not isinstance(value, list):
                        try:
                            value = json.loads(value)
                        except Exception:
                            value = []
                    setattr(player, field, value)
                elif field == 'clan':
                    if value:
                        from .models import Clan
                        try:
                            clan_obj = Clan.objects.get(pk=value)
                            player.clan = clan_obj
                        except Clan.DoesNotExist:
                            player.clan = None
                    else:
                        player.clan = None
                elif field in decimal_fields:
                    if value == "" or value is None:
                        setattr(player, field, None)
                    else:
                        setattr(player, field, value)
                else:
                    setattr(player, field, value)
            player.save()

            # Synchronize the ManyToMany 'players' field on Clan
            if 'clan' in data:
                # Remove from old clan's players if needed
                if old_clan and old_clan != player.clan:
                    old_clan.players.remove(player)
                # Add to new clan's players if not already present
                if player.clan and not player.clan.players.filter(pk=player.pk).exists():
                    player.clan.players.add(player)
                # Remove player from all other clans' players m2m except the new one
                from .models import Clan
                if player.clan:
                    other_clans = Clan.objects.filter(players=player).exclude(pk=player.clan.pk)
                else:
                    other_clans = Clan.objects.filter(players=player)
                for c in other_clans:
                    c.players.remove(player)

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False}, status=400)

def extract_raid_data_service(images, prompt, model_name='gemma-3-27b-it'):
    if len(images) < 1:
        return {'error': 'Please provide at least 1 image.', 'status': 400} 

    results = []

    # Get Google API key from environment variable
    api_key = os.environ.get("GOOGLE_API_KEY") or getattr(settings, "GOOGLE_API_KEY", None)
    if not api_key:
        return {'error': 'Google API key not set in environment variable GOOGLE_API_KEY or settings.', 'status': 500}
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(model_name)

    for image in images:
        image_bytes = image.read()
        image_parts = [{"mime_type": image.content_type, "data": base64.b64encode(image_bytes).decode()}]

        try:
            response = model.generate_content([prompt, *image_parts])
            raw_text = response.text.strip()
            match = re.search(r'(\{.*\}|\[.*\])', raw_text, re.DOTALL)
            if match:
                json_text = match.group(1)
                data = json.loads(json_text)
                results.append(data)
            else:
                results.append({'error': f'No JSON found in model response for image {image.name}. Raw response: {raw_text[:200]}', 'status': 400})
        except Exception as e:
            results.append({'error': f'Failed to process image {image.name}: {str(e)}', 'status': 500})

    return {'results': results, 'status': 200}

@csrf_exempt
# Request should include 'images' as a list of uploaded images
def extract_siege_post_data(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are accepted'}, status=405)

    images = request.FILES.getlist('images')

    prompt = (
        "Extract the post number and all choices from this image of a Raid Shadow Legends siege post. There should be a post number and a list of exactly 3 choices. "
        "The choices should be selected only from this list of valid team types: "
        f"{[choice[0] for choice in TEAM_CHOICES]}. "
        "Return only a JSON object like: {{\"Post\": <number>, \"Choices\": [\"choice1\", \"choice2\", ...]}}."
    )

    service_response = extract_raid_data_service(images, prompt)
    if 'error' in service_response:
        return JsonResponse({'error': service_response['error']}, status=service_response['status'])

   

    return JsonResponse(service_response['results'], safe=False)

@csrf_exempt
# Request should include 'images' as a list of uploaded images and 'clan_id' as a POST parameter
def extract_clash_player_data(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are accepted'}, status=405)

    images = request.FILES.getlist('images')
    clanPlayers = [player.name for player in Clan.objects.get(clan_id=request.POST.get('clan_id')).players.all()]
    print(clanPlayers)

    json_schema_string = """
            {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "List of User Accounts",
            "description": "A list of user accounts.",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                "Name": {
                    "type": "string"
                },
                "Score": {
                    "type": "number"
                },
                "Keys used": {
                    "type": "integer",
                    "enum": [0, 1, 2, 3]
                }
                },
                "required": [
                "Name",
                "Score",
                "Keys used"
                ]
            }
            }
            """
    
    prompt = f"""
        Extract the Player name, score and keys used, per player, from these images of a Raid Shadow Legends Clash Results page. 
        Scores are shown in the format "<decimal>B" (e.g. "1.5B" for 1.5 billion). and will only ever be 2 decimal places followed by "B" (billions) or "M" Millions.
        Make sure to convert the score to a decimal number, e.g. "1.5B" should be converted to 1500000000, and "150.5M" should be converted to 1505000000.
        Then format the score as a decimal with the unit strictly Billions (e.g. 1500000000 should be formatted as 1.5, 1505000000 should be formatted as 0.1505).
        The keys used are shown as a number from 0 to 3, representing the number of keys used by the player.
        The results should be returned as a JSON array of objects, each with "Name", "Score" and "Keys used" fields.
        The "Name" field should be the player's name, the "Score" field should be a decimal number, and the "Keys used" field should be an integer.
        The player names should be selected only from this list of valid players: 
        {clanPlayers}. 
        if a player is not in this list, they should not be included in the results.
        if a player is in the list but has no score, they should be included with a score of 0 and keys used of 0.
        Return only a JSON object that fits the following schema:
        {json_schema_string}
        
    """
    service_response = extract_raid_data_service(images, prompt)
    if 'error' in service_response:
        return JsonResponse({'error': service_response['error']}, status=service_response['status'])

     # Validate results against the JSON schema
    # try:
    #     schema = json.loads(json_schema_string)
    #     jsonschema.validate(instance=service_response['results'], schema=schema)
    # except Exception as e:
    #     return JsonResponse({'error': f'Result does not fit the JSON schema: {str(e)}'}, status=400)

    return JsonResponse(service_response['results'], safe=False)


def get_activity_scores(request, activity_type, record_id):
        if activity_type == 'hydra':
            try:
                record = HydraClash.objects.get(hydra_clash_id=record_id)
            except HydraClash.DoesNotExist:
                return JsonResponse({'error': 'Record not found'}, status=404)
            
        elif activity_type == 'chimera':
            try:
                record = ChimeraClash.objects.get(chimera_clash_id=record_id)
            except HydraClash.DoesNotExist:
                return JsonResponse({'error': 'Record not found'}, status=404)    
        else:
            return JsonResponse({'error': 'Invalid activity type'}, status=400)
        
        scores = record.clash_scores.values('player__name', 'score', 'keys_used', 'type')
        return JsonResponse({'scores': list(scores)})

@csrf_exempt
def create_clash_scores(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            activity_type = data.get('activity_type')
            activity_id = data.get('activity_id')
            scores = data.get('scores', [])

            if activity_type == 'hydra':
                activity = HydraClash.objects.get(hydra_clash_id=activity_id)
            elif activity_type == 'chimera':
                activity = ChimeraClash.objects.get(chimera_clash_id=activity_id)
            else:
                return JsonResponse({'error': 'Invalid activity type'}, status=400)

            for score_data in scores:
                print(score_data)
                player_id = score_data.get('Name')
                score = score_data.get('Score')
                keys_used = score_data.get('Keys used')
                player = Player.objects.get(name=player_id)

                # Check for existing ClashScore to prevent duplicates
                existing_score = ClashScore.objects.filter(
                    type=activity_type,
                    player=player,
                    hydra_activity=activity if activity_type == 'hydra' else None,
                    chimera_activity=activity if activity_type == 'chimera' else None
                ).first()

                if existing_score:
                    continue

                clash_score = ClashScore.objects.create(
                    type=activity_type,
                    player=player,
                    score=score,
                    keys_used=keys_used,
                    date_recorded=activity.date_recorded,
                    hydra_activity=activity if activity_type == 'hydra' else None,
                    chimera_activity=activity if activity_type == 'chimera' else None
                )

                activity.clash_scores.add(clash_score)

            return JsonResponse({'message': 'ClashScores created successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)