from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from .models import User, Team, Game, Round

class GameAndRoundTests(TestCase):
    def setUp(self):
        # Create test users with unique emails
        self.user1 = User.objects.create(username="Player1", email="player1@example.com")
        self.user2 = User.objects.create(username="Player2", email="player2@example.com")
        self.user3 = User.objects.create(username="Player3", email="player3@example.com")
        self.user4 = User.objects.create(username="Player4", email="player4@example.com")
        self.user5 = User.objects.create(username="Player5", email="player5@example.com")
        self.user6 = User.objects.create(username="Player6", email="player6@example.com")
        self.user7 = User.objects.create(username="Player7", email="player7@example.com")
        self.user8 = User.objects.create(username="Player8", email="player8@example.com")


        self.players_team1 = [self.user1.pk, self.user2.pk, self.user3.pk, self.user7.pk]
        self.players_team2 = [self.user4.pk, self.user5.pk, self.user6.pk, self.user8.pk]

    def test_create_game(self):
        url = reverse("start-game")
        data = {
            "game_settings": {"gamemode": "Casual", "teamsize": 4},
            "teams": {
                "team1": {"name": "Team A", "players": self.players_team1},
                "team2": {"name": "Team B", "players": self.players_team2}
            }
        }
        response = self.client.post(url, data, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Game.objects.exists())
        
    def test_create_round(self):
        # Create teams and game first
        team1 = Team.objects.create(team_name="Team A", player1=self.user1, player2=self.user2, player3=self.user3)
        team2 = Team.objects.create(team_name="Team B", player1=self.user4, player2=self.user5, player3=self.user6)
        game = Game.objects.create(team1=team1, team2=team2, team_size=3, gamemode="Casual")
        
        url = reverse("new-round") + f"?game_id={game.id}"
        data = {"gamestate": {"cups": {"1": "5", "2": "3", "10": "8"}}}
        response = self.client.post(url, data, content_type="application/json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Round.objects.count(), 1)
        self.assertEqual(Round.objects.first().round_number, 1)
