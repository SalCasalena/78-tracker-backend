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
    
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="game_team1")
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="game_team2")
    team_size = models.IntegerField(choices=[(3, "3"), (4, "4"), (5, "5"), (6, "6")])
    gamemode = models.CharField(max_length=20, choices=GAMEMODE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Not-Started")
    
    
    def __str__(self):
        formatted_time = self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else "Unknown Time"
        return f"{formatted_time}: {self.team1} vs {self.team2} | ({self.gamemode})"


class Round(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="rounds")
    players = models.ManyToManyField(User)

    def __str__(self):
        return f"Round {self.pk} of {self.game}"
    
