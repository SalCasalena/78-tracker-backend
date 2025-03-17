from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import User, Team, Game, Round, PlayerStats
from .serializers import GameStateSerializer, RoundSerializer
from rest_framework.exceptions import ValidationError

class GameStateView(APIView):
    def get(self, request, game_id):
        try:
            game = Game.objects.get(pk=game_id)
        except Game.DoesNotExist:
            return Response({"error": "Game not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = GameStateSerializer(game)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

                # Initialize PlayerStats for all players
                all_players = [team1.player1, team1.player2, team1.player3, team1.player4, team1.player5, team1.player6,
                               team2.player1, team2.player2, team2.player3, team2.player4, team2.player5, team2.player6]

                for player in filter(None, all_players):  # Remove `None` values
                    PlayerStats.objects.create(player=player, game=game)

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

class NewRoundView(APIView):
    def post(self, request, game_id):
        # Extract & Validate Game Data
        try:
            game = Game.objects.get(pk=game_id)
        except Game.DoesNotExist:
            return Response({"error": "Game not found."}, status=status.HTTP_404_NOT_FOUND)

        # **Update game status if this is the first round**
        if game.status == "Not-Started":
            game.status = "In-Progress"

        # Extract & Validate Cup Data
        data = request.data
        cups = data.get('gamestate', {}).get('cups', {})  # {cup_number: player_id}

        if not cups:
            return Response({"error": "Cup data is required."}, status=status.HTTP_400_BAD_REQUEST)

        # **Check for duplicate cups already hit**
        existing_cups = game.cups  # The current game state dictionary
        duplicate_cups = [cup for cup in cups.keys() if cup in existing_cups and existing_cups[cup] != ""]

        if duplicate_cups:
            return Response({
                "error": "Invalid cup data. Some cups were already hit.",
                "duplicate_cups": duplicate_cups
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get the next round number
        last_round = Round.objects.filter(game=game).order_by('-round_number').first()
        next_round_number = last_round.round_number + 1 if last_round else 1  # Start from 1 if no rounds exist

        # **Append New Cup Hits to Game State**
        updated_cups = game.cups.copy()  # Preserve old data
        updated_cups.update(cups)  # Append new hits
        game.cups = updated_cups  # Store updated state

        game.save()  # Triggers `save()` method to update stats
        
        # Here lets process indiual stats for each player
    
        
        

        # Create a new round record
        new_round = Round.objects.create(
            game=game,
            round_number=next_round_number,
            cups=cups,
            teamA_rack_status=game.teamA_rack_status,
            teamB_rack_status=game.teamB_rack_status
        )

        # **Build Response Data**
        response_data = {
            "message": "Round successfully recorded",
            "round_number": new_round.round_number,
            "cups": game.cups,  # Full cup state
            "teamA_cups_made": game.teamA_cups_made,
            "teamB_cups_made": game.teamB_cups_made,
            "teamA_cups_remaining": game.teamA_cups_remaining,
            "teamB_cups_remaining": game.teamB_cups_remaining,
            "teamA_rack_status": game.teamA_rack_status,
            "teamB_rack_status": game.teamB_rack_status
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
