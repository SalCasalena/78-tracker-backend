from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import User, Team, Game
from rest_framework.exceptions import ValidationError

class CreateGameView(APIView):
    def post(self, request):
        data = request.data
        
        # Extract game settings
        game_settings = data.get("game_settings", {})
        gamemode = game_settings.get("gamemode")
        team_size = game_settings.get("teamsize")

        if not gamemode or not team_size:
            return Response({"error": "Game mode and team size are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Extract teams
        teams_data = data.get("teams", {})
        team1_data = teams_data.get("team1")
        team2_data = teams_data.get("team2")

        if not team1_data or not team2_data:
            return Response({"error": "Both teams must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Create Team 1
                team1 = self.create_team(team1_data, team_size)

                # Create Team 2
                team2 = self.create_team(team2_data, team_size)

                # Create Game
                game = Game.objects.create(
                    team1=team1,
                    team2=team2,
                    team_size=team_size,
                    gamemode=gamemode
                )

            return Response({"message": "Game created successfully", "game_id": game.id}, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create_team(self, team_data, team_size):
        """Helper function to create a team."""
        team_name = team_data.get("name")
        player_pks = team_data.get("players", [])

        if not team_name or not player_pks:
            raise ValidationError("Team name and players are required.")

        if len(player_pks) != team_size:
            raise ValidationError(f"Team must have exactly {team_size} players.")

        players = list(User.objects.filter(pk__in=player_pks))
        if len(players) != team_size:
            raise ValidationError("Some provided player IDs do not exist.")

        # Create the team and assign players dynamically
        team = Team.objects.create(team_name=team_name, player1=players[0], player2=players[1], player3=players[2])

        if team_size >= 4:
            team.player4 = players[3]
        if team_size >= 5:
            team.player5 = players[4]
        if team_size == 6:
            team.player6 = players[5]

        team.save()
        return team
