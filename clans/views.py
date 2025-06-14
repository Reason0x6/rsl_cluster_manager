import logging
import django
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, DetailView
from .models import TEAM_CHOICES, ArenaTeam, Clan, Player, TeamType, CvC, HydraClash, ChimeraClash, Siege, LABattle, SiegePlan, PostAssignment
from .forms import PlayerForm, ClanForm, CvCForm, SiegeForm, HydraClashForm, ChimeraClashForm, SiegePlanForm, PostAssignmentForm, ArenaTeamForm
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from decimal import Decimal
from django.db.models import Avg, F

logger = logging.getLogger(__name__)

def home(request):
    players = Player.objects.all().order_by('name')
    clans = Clan.objects.prefetch_related('players').all().order_by('name')
    context = {
        'players': players,
        'clans': clans,
    }
    return render(request, 'clans/home.html', context)

def player_detail(request, uuid):  # Change from player_uuid to uuid
    player = get_object_or_404(Player, uuid=uuid)
    arena_teams = ArenaTeam.objects.filter(player=player)
    logger.info(f"{arena_teams}")
            
    context = {
        'player': player,
        'arena_teams': arena_teams,
        'all_team_types': TeamType.objects.all().order_by('name')
    }
    return render(request, 'clans/player_detail.html', context)

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

def clan_detail(request, clan_id):
    clan = get_object_or_404(Clan, clan_id=clan_id)
    
    # Calculate CvC Performance (wins vs total)
    cvc_records = [
        record for record in get_activities_config(clan)['CvC']['records']
    ]
    won_records = [
        record for record in cvc_records if record.score > record.opponent_score
    ]

    if cvc_records:
        # Win is when our score is higher than opponent score
        cvc_performance = (len(won_records) / len(cvc_records)) * 100
    else:
        cvc_performance = Decimal('0')


    # Calculate Siege Performance (position 1 = win)
    siege_records = clan.siege_records.all()
    if siege_records.exists():
        # Count records where position is 1 (wins)
        siege_wins = siege_records.filter(position=1).count()
        siege_performance = Decimal(str(siege_wins)) / Decimal(str(siege_records.count())) * 100
    else:
        siege_performance = Decimal('0')

    # Calculate Hydra Progress
    hydra_clashes = clan.hydra_clashes.all()
    if hydra_clashes.exists():
        # Calculate average position
        total_positions = sum(clash.rank for clash in hydra_clashes)
        avg_position = Decimal(str(total_positions)) / Decimal(str(hydra_clashes.count()))
        # Convert to percentage (1st = 100%, 5th = 0%)
        hydra_progress = max(Decimal('0'), 
            Decimal('100') * (Decimal('5') - avg_position) / Decimal('4'))
    else:
        hydra_progress = Decimal('0')

    # Calculate Chimera Progress
    chimera_clashes = clan.chimera_clashes.all()
    if chimera_clashes.exists():
        # Calculate average position
        total_positions = sum(clash.rank for clash in chimera_clashes)
        avg_position = Decimal(str(total_positions)) / Decimal(str(chimera_clashes.count()))
        # Convert to percentage (1st = 100%, 5th = 0%)
        chimera_progress = max(Decimal('0'), 
            Decimal('100') * (Decimal('5') - avg_position) / Decimal('4'))
    else:
        chimera_progress = Decimal('0')

    context = {
        'clan': clan,
        'activities_config': get_activities_config(clan),
        'cvc_performance': round(float(cvc_performance), 1),
        'hydra_progress': round(float(hydra_progress), 1),
        'chimera_progress': round(float(chimera_progress), 1),
        'siege_performance': round(float(siege_performance), 1),
    }
    return render(request, 'clans/clan_detail.html', context)

def clan_edit(request, clan_id):
    clan = get_object_or_404(Clan, clan_id=clan_id)
    if request.method == 'POST':
        form = ClanForm(request.POST, instance=clan)
        if form.is_valid():
            form.save()
            return redirect('clan_detail', clan_id=clan.clan_id)
    else:
        form = ClanForm(instance=clan)
    context = {'form': form, 'clan': clan, 'action': 'Edit'}
    return render(request, 'clans/clan_form.html', context)

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

class PlayerListView(ListView):
    model = Player
    template_name = 'clans/player_list.html'
    context_object_name = 'players'
    
    def get_queryset(self):
        return Player.objects.all().prefetch_related('clans')

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
def delete_player(request, player_uuid):
    try:
        player = get_object_or_404(Player, uuid=player_uuid)
        player.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def calculate_performance(clan):
    # Example calculations - adjust based on your actual data
    cvc_performance = (
        clan.cvcrecord_set.filter(personal_rewards=True).count() /
        clan.cvcrecord_set.count() * 100 if clan.cvcrecord_set.exists() else 0
    )
    
    hydra_progress = (
        clan.hydrarecord_set.aggregate(Avg('opponent_scores'))['score__avg'] /
        clan.hydra_clash_required_score * 100 if clan.hydrarecord_set.exists() else 0
    )
    
    return cvc_performance, hydra_progress

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
def import_players(request):
    try:
        data = json.loads(request.body)
        imported_count = 0
        
        for player_data in data:
            name = player_data.get('name')
            if not name:
                continue
                
            # Create or update player
            player, created = Player.objects.update_or_create(
                player_id_ingame=name,  # Using name as ingame ID
                defaults={
                    'name': name,
                    'player_power': player_data.get('player_power', 0)
                }
            )
            imported_count += 1
            
        return JsonResponse({
            'status': 'success',
            'imported': imported_count
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

# Add this new view function
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
            'level': player.level or 0,
            'player_power': float(player.player_power or 0),
            'player_id_ingame': player.player_id_ingame or '',
            'discord_id': player.discord_id or ''
        } for player in players]
        
        return JsonResponse({
            'status': 'success',
            'players': players_data,
            'total_count': clan.players.count()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

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
def export_siege_plan(request, plan_id):
    siege_plan = get_object_or_404(SiegePlan, id=plan_id)
    assignments = siege_plan.assignments.all()
    return render(request, 'clans/export_siege_plan.html', {'siege_plan': siege_plan, 'assignments': assignments})

@csrf_exempt
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
