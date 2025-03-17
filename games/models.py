from django.db import models
from users.models import User

class Team(models.Model):
    team_name = models.CharField(max_length=100, unique=False)
    player1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="team_player1")
    player2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="team_player2")
    player3 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="team_player3")
    player4 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="team_player4")
    player5 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="team_player5")
    player6 = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="team_player6")

    def __str__(self):
        return self.team_name
    
class Game(models.Model):
    GAMEMODE_CHOICES = [
        ('Casual', 'Casual'),
        ('Competitive', 'Competitive'),
        ('IFC', 'IFC'),
    ]
    STATUS_CHOICES = [
        ('Not-Started', 'Not-Started'),
        ('In-Progress', 'In-Progress'),
        ('Completed', 'Completed'),
    ]
    RACK_STATUS_CHOICES = [
        ('Initial', 'Initial'),
        ('Rerack', 'Rerack'),
        ('Zipper-7', 'Zipper-7'),
        ('Zipper-9', 'Zipper-9'),
        ('Gentlemans', 'Gentlemans'),
    ]
    
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="game_team1")
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="game_team2")
    team_size = models.IntegerField(choices=[(3, "3"), (4, "4"), (5, "5"), (6, "6")])
    gamemode = models.CharField(max_length=20, choices=GAMEMODE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Not-Started")
    teamA_rack_status = models.CharField(max_length=20, choices=RACK_STATUS_CHOICES, default="Initial")
    teamB_rack_status = models.CharField(max_length=20, choices=RACK_STATUS_CHOICES, default="Initial")

    # Team Statistics (Game Level)
    teamA_cups_made = models.IntegerField(default=0)
    teamB_cups_made = models.IntegerField(default=0)
    teamA_cups_remaining = models.IntegerField(default=78)
    teamB_cups_remaining = models.IntegerField(default=78)
    
    # Game State
    cups = models.JSONField(default=dict)  

    def __str__(self):
        return f"{self.team1} vs {self.team2} | {self.status}"
    
    def determine_rack_status(self, remaining_cups):
        """Auto-determine rack status based on remaining cups."""
        if remaining_cups <= 2:
            return "Gentlemans"
        elif remaining_cups <= 7:
            return "Zipper-7"
        elif remaining_cups <= 21:
            return "Rerack"
        return "Initial"

    def process_game_stats(self):
        """Processes the game state to update team stats based on made cups."""
        teamA_made = 0
        teamB_made = 0

        for cup_number, player_id in self.cups.items():
            cup_number = int(cup_number)
            if player_id:  # If a cup was made
                if cup_number >= 79:
                    teamA_made += 1
                else:
                    teamB_made += 1

        # Update team statistics
        self.teamA_cups_made = teamA_made
        self.teamB_cups_made = teamB_made
        self.teamA_cups_remaining = 78 - teamA_made
        self.teamB_cups_remaining = 78 - teamB_made  # Team A makes a shot, reducing Team B's remaining cups

        # Update rack status automatically
        self.teamA_rack_status = self.determine_rack_status(self.teamA_cups_remaining)
        self.teamB_rack_status = self.determine_rack_status(self.teamB_cups_remaining)
    
    def save(self, *args, **kwargs):
        """Override save method to automatically process game stats."""
        self.process_game_stats()
        super().save(*args, **kwargs)

        


class Round(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="rounds")
    round_number = models.IntegerField()
    cups = models.JSONField(default=dict)  # Track which player made which cup
    teamA_rack_status = models.CharField(max_length=20, choices=Game.RACK_STATUS_CHOICES, default="Initial")
    teamB_rack_status = models.CharField(max_length=20, choices=Game.RACK_STATUS_CHOICES, default="Initial")

    def __str__(self):
        return f"Round {self.round_number} of {self.game}"

class PlayerStats(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name="player_stats")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="game_stats")
    
    # Individual Player Statistics
    shots_taken = models.IntegerField(default=0)
    cups_made = models.IntegerField(default=0)
    own_cups = models.IntegerField(default=0)  # Own team's cups mistakenly hit
    accuracy = models.FloatField(default=0.0)
    
    death_cups = models.IntegerField(default=0)
    clutch_cups = models.IntegerField(default=0)

    class Meta:
        unique_together = ('player', 'game')  # Prevents duplicate player stats per game

    def save(self, *args, **kwargs):
        """Automatically update accuracy on save."""
        self.accuracy = (self.cups_made / self.shots_taken * 100) if self.shots_taken > 0 else 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.player.username}[{self.pk}] [Game: {self.game.id}] {self.cups_made} | {self.shots_taken} | {self.accuracy}%"
