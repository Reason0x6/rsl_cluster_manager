import uuid
from django.db import models
from django.utils import timezone # For potential date fields
from django.core.validators import MinValueValidator, MaxValueValidator
import json
from django.contrib.postgres.fields import JSONField  # For storing JSON data
from django.contrib import admin
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal



class Player(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    player_power = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Enter player power in millions (e.g., 4.5 for 4.5M)"
    )
    hydra_clash_score = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Hydra Clash score in billions (e.g., 4.5 for 4.5B)"
    )
    hydra_difficulty = models.CharField(
        max_length=20,
        choices=[('NM', 'NM'), ('B', 'B'), ('H', 'H')],
        blank=True,
        null=True
    )
    hydra_difficulty_multi = models.JSONField(default=list, blank=True)  # For multi-select

    chimera_clash_score = models.DecimalField(
        max_digits=7,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Chimera Clash score in billions"
    )
    chimera_difficulty = models.CharField(
        max_length=20,
        choices=[('UNM', 'UNM'), ('NM', 'NM'), ('B', 'B'), ('H', 'H')],
        blank=True,
        null=True
    )
    chimera_difficulty_multi = models.JSONField(default=list, blank=True)  # For multi-select

    siege = models.CharField(
        max_length=20,
        choices=[('Competitive', 'Competitive'), ('Strong', 'Strong'), ('Good', 'Good'), ('Limited', 'Limited'), ('Weak', 'Weak')],
        blank=True,
        null=True
    )
    activity = models.CharField(
        max_length=20,
        choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')],
        blank=True,
        null=True
    )
    dependability = models.CharField(
        max_length=20,
        choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')],
        blank=True,
        null=True
    )
    ranking_points = models.FloatField(null=True, blank=True)
    hh_optimiser_link = models.URLField(null=True, blank=True)
    development_notes = models.TextField(blank=True, null=True)
    team_types = models.ManyToManyField('TeamType', related_name='players', blank=True)
    clan = models.ForeignKey(
        'Clan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='player_set'  # Changed from 'players' to 'player_set' to avoid clash
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def hydra_clash_score(self):
        clash_scores = self.clash_scores.filter(type="hydra").values_list("score", flat=True)
        return round(sum(clash_scores) / len(clash_scores), 2) if clash_scores else None

    @property
    def chimera_clash_score(self):
        clash_scores = self.clash_scores.filter(type="chimera").values_list("score", flat=True)
        return round(sum(clash_scores) / len(clash_scores), 2) if clash_scores else None

    @property
    def calculate_ranking_points(self):
        # Fetch general settings for weights
        settings = GeneralSettings.objects.first()
        hydra_weight = Decimal(settings.hydra_weight if settings else 0.3)
        chimera_weight = Decimal(settings.chimera_weight if settings else 0.7)

        # Handle missing data
        hydra_avg = Decimal(self.hydra_clash_score or 0)
        chimera_avg = Decimal(self.chimera_clash_score or 0)

        # Fetch all players' scores for normalization
        all_players = Player.objects.all()
        hydra_scores = [Decimal(player.hydra_clash_score or 0) for player in all_players]
        chimera_scores = [Decimal(player.chimera_clash_score or 0) for player in all_players]

        # Min-Max normalization
        hydra_min, hydra_max = min(hydra_scores, default=Decimal(0)), max(hydra_scores, default=Decimal(1))
        chimera_min, chimera_max = min(chimera_scores, default=Decimal(0)), max(chimera_scores, default=Decimal(1))

        hydra_norm = (hydra_avg - hydra_min) / (hydra_max - hydra_min) if hydra_max != hydra_min else Decimal(0)
        chimera_norm = (chimera_avg - chimera_min) / (chimera_max - chimera_min) if chimera_max != chimera_min else Decimal(0)

        # Weighted sum
        return round((hydra_norm * hydra_weight) + (chimera_norm * chimera_weight), 4)

    def save(self, *args, **kwargs):
        # Calculate ranking points
        self.ranking_points = self.calculate_ranking_points  # Remove parentheses
        super().save(*args, **kwargs)

    
class Clan(models.Model):
    CLAN_BOSS_LEVELS = [
        ('easy', 'Easy'),
        ('normal', 'Normal'),
        ('hard', 'Hard'),
        ('brutal', 'Brutal'),
        ('nightmare', 'Nightmare'),
        ('ultra_nightmare', 'Ultra Nightmare'),
    ]

    clan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    clan_boss_level = models.CharField(
        max_length=255,
        help_text="Clan Boss levels down",
        default='[]'
    )
    hydra_clash_required_score = models.DecimalField(
        max_digits=7,  # Allows numbers up to 9999.999 billion
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Enter score in billions (e.g., 1.5 for 1.5B)"
    )
    chimera_clash_required_score = models.DecimalField(
        max_digits=7,  # Allows numbers up to 9999.999 billion
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Enter score in billions (e.g., 1.5 for 1.5B)"
    )
    personal_rewards_cvc_threshold = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        null=True, 
        blank=True
    )
    non_pr_cvc_threshold = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        null=True, 
        blank=True
    )
    clan_level = models.PositiveIntegerField()
    players = models.ManyToManyField(Player, related_name='clans', blank=True)

    def __str__(self):
        return self.name

    @property
    def total_power(self):
        """Calculate total player power for all clan members"""
        return self.players.aggregate(
            total=models.Sum('player_power', default=0)
        )['total'] or 0

    def get_boss_levels(self):
        """Returns list of boss levels"""
        import json
        try:
            return json.loads(self.clan_boss_level)
        except:
            return []

    def set_boss_levels(self, levels):
        """Sets boss levels from list"""
        import json
        self.clan_boss_level = json.dumps(levels)

    def get_boss_levels_display(self):
        """Returns formatted string of boss levels"""
        if not self.clan_boss_level:
            return "None"
            
        try:
            levels = json.loads(self.clan_boss_level)
            if not levels:
                return "None"
                
            # Convert each level to title case and replace underscores
            formatted_levels = [level.replace('_', ' ').title() for level in levels]
            return ", ".join(formatted_levels)
        except json.JSONDecodeError:
            return "None"
        except AttributeError:
            return "None"

class CvC(models.Model):
    cvc_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clan = models.ForeignKey(Clan, related_name='cvcs', on_delete=models.CASCADE)
    opponent = models.CharField(max_length=100)
    tier = models.PositiveIntegerField()
    score = models.PositiveIntegerField()
    opponent_score = models.PositiveIntegerField()
    personal_rewards = models.BooleanField(default=False)
    date_recorded = models.DateTimeField(default=timezone.now) # Added for sorting

    def __str__(self):
        return f"CvC: {self.clan.name} vs {self.opponent} (Tier {self.tier}) - {self.date_recorded.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-date_recorded']


class Siege(models.Model):
    siege_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clan = models.ForeignKey('Clan', on_delete=models.CASCADE, related_name='siege_records')
    position = models.PositiveIntegerField(
        help_text="Final position in the Siege",
        default=0
    )
    points = models.PositiveIntegerField(
        help_text="Total points earned in the Siege",
        default=0
    )
    opponent_clan = models.CharField(
        max_length=100,
        help_text="Name of the opponent clan",
        blank=True,
        null=True
    )
    opponent_score = models.PositiveIntegerField(
        help_text="Score of the opponent clan",
        default=0
    )
    result = models.CharField(
        max_length=10, 
        choices=[('win', 'Win'), ('loss', 'Loss')],
        default='loss'
    )
    date_recorded = models.DateTimeField(
        default=timezone.now,
        help_text="When this Siege occurred"
    )

    class Meta:
        ordering = ['-date_recorded']

    def __str__(self):
        return f"Siege: {self.clan.name} vs {self.opponent_clan} - Position {self.position} ({self.date_recorded.strftime('%Y-%m-%d')})"

class HydraClash(models.Model):
    hydra_clash_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='hydra_clashes')
    opponent_scores = models.JSONField(default=dict)
    date_recorded = models.DateTimeField(default=timezone.now)
    clash_scores = models.ManyToManyField('ClashScore', related_name='hydra_clashes', blank=True, limit_choices_to={'clash_scores__count__lte': 30})

    class Meta:
        ordering = ['-date_recorded']

    def __str__(self):
        return f"Hydra Clash: {self.clan.name} ({self.date_recorded.strftime('%Y-%m-%d')})"

    @property
    def scores_display(self):
        """Format opponent scores for admin display"""
        return ', '.join(f"{k}: {v}" for k, v in self.opponent_scores.items())

    @property
    def get_top_3_scores(self):
        """
        Returns the top 3 (clan, score) tuples ordered by score descending from opponent_scores.
        """
        scores = []
        for score in self.opponent_scores.items():
            scores.append(score[1])
                    
        return sorted(scores, reverse=True)[:3]

    @property
    def rank(self):
        """Calculate rank based on scores"""
        try:
            # Convert scores to float, skip invalid entries
            scores = []
            for clan, score in self.opponent_scores.items():
                try:
                    score_value = float(score) if isinstance(score, (int, float, str)) else 0
                    scores.append((clan, score_value))
                except (ValueError, TypeError):
                    continue
            
            # Sort scores and find our clan's position
            sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
            for index, (clan, _) in enumerate(sorted_scores, 1):
                if clan == self.clan.name:
                    return index
            return len(scores)
        except Exception:
            return 0

    def get_clan_score(self):
        """Return the clan's score from the opponent_scores JSON field."""
        try:
            return float(self.opponent_scores.get(self.clan.name, 0))
        except (ValueError, TypeError):
            return 0

class ChimeraClash(models.Model):
    chimera_clash_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='chimera_clashes')
    opponent_scores = models.JSONField(default=dict)
    date_recorded = models.DateTimeField(default=timezone.now)
    clash_scores = models.ManyToManyField('ClashScore', related_name='chimera_clashes', blank=True, limit_choices_to={'clash_scores__count__lte': 30})

    class Meta:
        ordering = ['-date_recorded']

    def __str__(self):
        return f"Chimera Clash: {self.clan.name} ({self.date_recorded.strftime('%Y-%m-%d')})"
    
    @property
    def get_top_3_scores(self):
        """
        Returns the top 3 (clan, score) tuples ordered by score descending from opponent_scores.
        """
        scores = []
        for score in self.opponent_scores.items():
            scores.append(score[1])
                    
        return sorted(scores, reverse=True)[:3]
        
    @property
    def scores_display(self):
        """Format opponent scores for admin display"""
        return ', '.join(f"{k}: {v}" for k, v in self.opponent_scores.items())

    @property
    def rank(self):
        """Calculate rank based on scores"""
        try:
            # Convert scores to float, skip invalid entries
            scores = []
            for clan, score in self.opponent_scores.items():
                try:
                    score_value = float(score) if isinstance(score, (int, float, str)) else 0
                    scores.append((clan, score_value))
                except (ValueError, TypeError):
                    continue
            
            # Sort scores and find our clan's position
            sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
            for index, (clan, _) in enumerate(sorted_scores, 1):
                if clan == self.clan.name:
                    return index
            return len(scores)
        except Exception:
            return 0
        
    def get_clan_score(self):
        """Return the clan's score from the opponent_scores JSON field."""
        try:
            return float(self.opponent_scores.get(self.clan.name, 0))
        except (ValueError, TypeError):
            return 0
        
TEAM_CHOICES = [
    # Factions
    ('banner_lords', 'Banner Lords'),
    ('high_elves', 'High Elves'),
    ('sacred_order', 'Sacred Order'),
    ('barbarians', 'Barbarians'),
    ('ogryn_tribes', 'Ogryn Tribes'),
    ('lizardmen', 'Lizardmen'),
    ('skinwalkers', 'Skinwalkers'),
    ('orcs', 'Orcs'),
    ('demonspawn', 'Demonspawn'),
    ('undead_hordes', 'Undead Hordes'),
    ('dark_elves', 'Dark Elves'),
    ('knight_revenant', 'Knights Revenant'),
    ('dwarves', 'Dwarves'),
    ('shadowkin', 'Shadowkin'),
    ('sylvan_watchers', 'Sylvan Watchers'),
    
    # Alliances
    ('telerian_alliance', 'Telerian League'),
    ('gaellen_pact', 'Gaellen Pact'),
    ('corrupted', 'The Corrupted'),
    ('nyresan_union', 'Nyresan Union'),

    # Affinities
    ('void', 'Void'),
    ('spirit', 'Spirit'),
    ('magic', 'Magic'),
    ('force', 'Force'),

    # Roles
    ('support', 'Support'),
    ('attack', 'ATK'),
    ('defense', 'DEF'),
    ('hp', 'HP'),

    # Rarities
    ('legendary', 'Legendary Champions'),
    ('epic', 'Epic Champions'),
    ('rare', 'Rare Champions'),

    # Immunities & Special Rules
    ('immune_turn_meter_reduction', 'Immunity - TM Reduction'),
    ('immune_turn_meter_boosting', 'Immunity - TM Boosting'),
    ('immune_cooldowns_increasing', 'Immunity - Ability Cooldown Increasing'),
    ('immune_cooldowns_decreasing', 'Immunity - Ability Cooldown Decreasing'),
    ('immune_sheep', 'Immunity - Sheep'),
    ('no_revive', "Champions Can't Be Revived"),
]


class TeamType(models.Model):
    name = models.CharField(max_length=50, choices=TEAM_CHOICES, unique=True)
    def __str__(self):
        # Avoid KeyError for missing choices
        return dict(TEAM_CHOICES).get(self.name, self.name)

    @classmethod
    def remove_orphaned_from_players(cls):
        # Remove team types from players if the TeamType does not exist
        valid_names = set(cls.objects.values_list('name', flat=True))
        for player in Player.objects.all():
            player_team_types = player.team_types.values_list('name', flat=True)
            to_remove = [tt for tt in player_team_types if tt not in valid_names]
            if to_remove:
                player.team_types.remove(*TeamType.objects.filter(name__in=to_remove))

    @classmethod
    def remove_by_name_or_value(cls, identifier):
        """
        Remove a TeamType by its name (code) or display value.
        Also removes the team type from all players.
        Usage:
            TeamType.remove_by_name_or_value('banner_lords')
            TeamType.remove_by_name_or_value('Banner Lords')
        """
        # Try to match by code (name)
        team_type = cls.objects.filter(name=identifier).first()
        if not team_type:
            # Try to match by display value
            code = None
            for code_candidate, display in TEAM_CHOICES:
                if display.lower() == identifier.lower():
                    code = code_candidate
                    break
            if code:
                team_type = cls.objects.filter(name=code).first()
        if team_type:
            # Remove from all players
            for player in team_type.players.all():
                player.team_types.remove(team_type)
            team_type.delete()
            return True
        return False

class LABattle(models.Model):
    battle_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='la_battles')
    opponent_name = models.CharField(max_length=100)
    points_change = models.IntegerField(help_text="Points gained (positive) or lost (negative)")
    my_champions = models.JSONField(
        default=list,
        help_text="List of champions used by the player"
    )
    opponent_champions = models.JSONField(
        default=list,
        help_text="List of champions used by the opponent"
    )
    date_recorded = models.DateTimeField(default=timezone.now)
    current_points = models.IntegerField(help_text="Total points after this battle")

    class Meta:
        ordering = ['-date_recorded']

    def __str__(self):
        return f"{self.player.name} vs {self.opponent_name} ({self.points_change:+d}pts)"

class SiegePlan(models.Model):
    clan = models.ForeignKey('Clan', on_delete=models.CASCADE, related_name='siege_plans')
    name = models.CharField(max_length=100)
    plan_data = models.JSONField()  # Updated to use django.db.models.JSONField
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.clan.name})"

class PostAssignment(models.Model):
    siege_plan = models.ForeignKey(SiegePlan, on_delete=models.CASCADE, related_name='assignments')
    post_number = models.IntegerField()
    team_choice = models.CharField(max_length=50, choices=TEAM_CHOICES)
    assigned_player = models.ForeignKey('Player', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Post {self.post_number} - {self.team_choice} ({self.siege_plan.name})"
    

class ArenaTeam(models.Model):
    team_type = models.ForeignKey('TeamType', on_delete=models.CASCADE, related_name='arena_teams')
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='arena_teams')
    champions = models.JSONField(default=list, help_text="List of champion names")

    def __str__(self):
        return f"{self.team_type} - {self.player.name}"

class ClashScore(models.Model):
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='clash_scores')
    score = models.DecimalField(
        max_digits=7,  # Allows numbers up to 9999.999 billion
        decimal_places=3,
        help_text="Score in billions (e.g., 1.5 for 1.5B)"
    )
    keys_used = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(3)],
        help_text="Number of keys used (0 to 3)"
    )
    date_recorded = models.DateTimeField(default=timezone.now, help_text="Date when the score was recorded")
    type = models.CharField(
        max_length=20,
        choices=[('hydra', 'Hydra'), ('chimera', 'Chimera')],
        help_text="Type of clash score (Hydra or Chimera)"
    )
    hydra_activity = models.ForeignKey(
        'HydraClash',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='hydra_clash_scores',
        help_text="Hydra Clash activity associated with this score"
    )
    chimera_activity = models.ForeignKey(
        'ChimeraClash',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='chimera_clash_scores',
        help_text="Chimera Clash activity associated with this score"
    )

    class Meta:
        ordering = ['-date_recorded']

    def __str__(self):
        return f"{self.player.name} - {self.score}B ({self.keys_used} keys)"

class ClashScoreAdmin(admin.ModelAdmin):
    list_display = ('player', 'score', 'keys_used', 'date_recorded')
    search_fields = ('player__name',)
    list_filter = ('date_recorded',)

admin.site.register(ClashScore, ClashScoreAdmin)

# Register all models in the admin panel
admin.site.register(LABattle)
admin.site.register(SiegePlan)
admin.site.register(PostAssignment)
admin.site.register(ArenaTeam)

class GeneralSettings(models.Model):
    hydra_weight = models.FloatField(
        default=0.3,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Weight for Hydra average in ranking calculation (0 to 1)"
    )
    chimera_weight = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Weight for Chimera average in ranking calculation (0 to 1)"
    )

    def __str__(self):
        return "General Settings"

    class Meta:
        verbose_name = "General Setting"
        verbose_name_plural = "General Settings"

        
admin.site.register(GeneralSettings)

@receiver(post_save, sender=GeneralSettings)
def recalculate_all_rankings(sender, instance, **kwargs):
    # Fetch all players and update their ranking points
    for player in Player.objects.all():
        player.ranking_points = player.calculate_ranking_points
        player.save(update_fields=['ranking_points'])

@receiver(post_save, sender=Player)
def update_ranking_points(sender, instance, **kwargs):
    if 'ranking_points' not in kwargs.get('update_fields', []):
        instance.ranking_points = instance.calculate_ranking_points
        instance.save(update_fields=['ranking_points'])