import uuid
from django.db import models
from django.utils import timezone # For potential date fields
from django.core.validators import MinValueValidator, MaxValueValidator
import json
from django.contrib.postgres.fields import JSONField  # For storing JSON data

class Player(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    level = models.IntegerField(null=True, blank=True)
    hh_optimiser_link = models.URLField(null=True, blank=True)
    player_power = models.DecimalField(
        max_digits=10,  # Allows numbers up to 99.999999 million
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Enter player power in millions (e.g., 4.5 for 4.5M)"
    )
    player_id_ingame = models.CharField(max_length=50, unique=True)
    discord_id = models.CharField(max_length=100, null=True, blank=True)
    clan = models.ForeignKey(
        'Clan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='player_clan'  # Updated related_name
    )
    team_types = models.ManyToManyField('TeamType', related_name='players', blank=True)

    current_points = models.IntegerField(default=0)

    def __str__(self):
        return self.name

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

    class Meta:
        ordering = ['-date_recorded']

    def __str__(self):
        return f"Hydra Clash: {self.clan.name} ({self.date_recorded.strftime('%Y-%m-%d')})"

    @property
    def scores_display(self):
        """Format opponent scores for admin display"""
        return ', '.join(f"{k}: {v}" for k, v in self.opponent_scores.items())

    @property
    def score(self):
        """Get our clan's score from the opponent_scores JSON field"""
        try:
            score = self.opponent_scores.get(self.clan.name, 0)
            return float(score) if isinstance(score, (int, float, str)) else 0
        except (ValueError, TypeError):
            return 0

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

class ChimeraClash(models.Model):
    chimera_clash_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='chimera_clashes')
    opponent_scores = models.JSONField(default=dict)
    date_recorded = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_recorded']

    def __str__(self):
        return f"Chimera Clash: {self.clan.name} ({self.date_recorded.strftime('%Y-%m-%d')})"

    @property
    def scores_display(self):
        """Format opponent scores for admin display"""
        return ', '.join(f"{k}: {v}" for k, v in self.opponent_scores.items())

    @property
    def score(self):
        """Get our clan's score from the opponent_scores JSON field"""
        try:
            score = self.opponent_scores.get(self.clan.name, 0)
            return float(score) if isinstance(score, (int, float, str)) else 0
        except (ValueError, TypeError):
            return 0

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
        return dict(TEAM_CHOICES)[self.name]


class CvCRecord(models.Model):
    clan = models.ForeignKey('Clan', on_delete=models.CASCADE, related_name='cvc_records')
    date_recorded = models.DateField()
    opponent = models.CharField(max_length=100)
    score = models.IntegerField()
    opponent_score = models.IntegerField()
    personal_rewards = models.BooleanField(default=False)
    tier = models.CharField(max_length=50)

    class Meta:
        ordering = ['-date_recorded']

class HydraRecord(models.Model):
    clan = models.ForeignKey('Clan', on_delete=models.CASCADE, related_name='hydra_history')  # Changed from hydra_records
    date_recorded = models.DateField()
    score = models.FloatField()
    difficulty = models.CharField(max_length=50)

    class Meta:
        ordering = ['-date_recorded']

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