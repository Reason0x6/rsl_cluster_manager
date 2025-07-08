from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Existing URL patterns
    path('', views.home, name='home'),
    path('players/', views.PlayerListView.as_view(), name='player_list'),
    path('player/<uuid:uuid>/', views.player_detail, name='player_detail'),
    path('player/<uuid:uuid>/edit/', views.player_edit, name='player_edit'),
    path('player/create/', views.player_create, name='player_create'),
    
    # Clan URLs
    path('clan/<uuid:clan_id>/', views.clan_detail, name='clan_detail'),
    path('clan/<uuid:clan_id>/edit/', views.clan_edit, name='clan_edit'),
    path('clan/create/', views.clan_create, name='clan_create'),

    # Activity URLs - Create
    path('clan/<uuid:clan_id>/cvc/create/', views.cvc_create, name='cvc_create'),
    path('clan/<uuid:clan_id>/hydra/create/', views.hydra_clash_create, name='hydra_clash_create'),
    path('clan/<uuid:clan_id>/chimera/create/', views.chimera_clash_create, name='chimera_clash_create'),
    path('clan/<uuid:clan_id>/siege/create/', views.siege_create, name='siege_create'),

    # Activity URLs - Edit
    path('cvc/<uuid:cvc_id>/edit/', views.cvc_edit, name='cvc_edit'),
    path('hydra/<uuid:hydra_clash_id>/edit/', views.hydra_clash_edit, name='hydra_clash_edit'),  # Changed from hydra_id
    path('chimera/<uuid:chimera_id>/edit/', views.chimera_clash_edit, name='chimera_clash_edit'),
    path('siege/<uuid:siege_id>/edit/', views.siege_edit, name='siege_edit'),

    # Activity URLs - Delete
    path('activity/<str:activity_type>/<uuid:record_id>/delete/', views.delete_activity, name='delete_activity'),

    # API endpoints
    path('api/activities/<str:activity_type>/<uuid:record_id>/', views.delete_activity, name='api_delete_activity'),

    # Player management URLs
    path('player/<uuid:player_uuid>/delete/', views.delete_player, name='delete_player'),
    path('player/<uuid:player_uuid>/teams/', views.manage_player_teams, name='manage_player_teams'),
    path('player/<uuid:player_uuid>/teams/<int:team_id>/', views.manage_player_teams, name='remove_player_team'),
    path('player/<uuid:player_uuid>/arena-teams/', views.manage_arena_teams, name='manage_arena_teams'),

    # Import players API
    path('api/player/import/', views.import_players, name='import_players'),

    # Get players in a clan
    path('api/clan/<uuid:clan_id>/players/', views.get_clan_players, name='get_clan_players'),

    # LA Tracker URL
    path('la-tracker/', views.la_tracker, name='la_tracker'),

    # LA Battle API endpoints
    path('api/player/<uuid:player_id>/la-battles/', views.la_battle_create, name='la_battle_create'),
    path('api/la-battles/<uuid:battle_id>/', views.la_battle_detail, name='la_battle_detail'),

    # Siege Plan URLs
    path('clan/<uuid:clan_id>/siege-plan/create/', views.create_siege_plan, name='create_siege_plan'),
    path('siege-plan/<int:plan_id>/assign/', views.assign_siege_plan, name='assign_siege_plan'),
    path('siege-plan/<int:plan_id>/export/', views.export_siege_plan, name='export_siege_plan'),
    path('siege-plan/<int:plan_id>/delete/', views.delete_siege_plan, name='delete_siege_plan'),

    # New URL patterns
    path('manage/', views.manage_clans, name='manage_clans'),
    path('update_player_field/<uuid:player_id>/', views.update_player_field, name='update_player_field'),
    path('update_player_data/<uuid:player_id>/', views.update_player_data, name='update_player_data'),

    # Login and logout URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
]