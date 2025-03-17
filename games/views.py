from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import User, Team, Game, Round, PlayerStats
from .serializers import GameStateSerializer, RoundResponseSerializer
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
            
        # Make sure the game is not completed
        if game.status == "Completed":
            return Response({"error": "Game is already completed."}, status=status.HTTP_400_BAD_REQUEST)

        # Extract & Validate Cup Data
        data = request.data
        cups = data.get('gamestate', {}).get('cups', {})  # {cup_number: player_id}
        deathcups = data.get('gamestate', {}).get('deathcups', [])  # {cup_number: player_id}

        if not cups:
            return Response({"error": "Cup data is required."}, status=status.HTTP_400_BAD_REQUEST)

        # **Check for duplicate cups already hit**
        existing_cups = game.cups
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
        updated_cups = game.cups.copy()
        updated_cups.update(cups)
        game.cups = updated_cups
        
        # Chec if the game is completed
        if len(updated_cups) >= 78:
            game.status = "Completed"

        # **Ensure PlayerStats exists for all players**
        all_players = [
            game.team1.player1, game.team1.player2, game.team1.player3,
            game.team1.player4, game.team1.player5, game.team1.player6,
            game.team2.player1, game.team2.player2, game.team2.player3,
            game.team2.player4, game.team2.player5, game.team2.player6
        ]
        all_players = [player for player in all_players if player is not None]

        for player in all_players:
            player_stats, _ = PlayerStats.objects.get_or_create(player=player, game=game)
            player_stats.shots_taken += 1
            player_stats.save()

        # **Process Individual Player Stats (Only If They Hit a Cup)**
        teamA_cup_hitters = []
        teamB_cup_hitters = []
        
        for cup, player_id in cups.items():
            try:
                player = User.objects.get(pk=player_id)
                player_stats, _ = PlayerStats.objects.get_or_create(player=player, game=game)

                if int(cup) < 79:
                    # Cup belongs to Team A, so the shooter must be on Team B
                    if player in [
                        game.team2.player1, game.team2.player2, game.team2.player3,
                        game.team2.player4, game.team2.player5, game.team2.player6
                    ]:
                        player_stats.cups_made += 1
                        teamB_cup_hitters.append(player)
                    else:
                        player_stats.own_cups += 1
                elif int(cup) > 78:
                    # Cup belongs to Team B, so the shooter must be on Team A
                    if player in [
                        game.team1.player1, game.team1.player2, game.team1.player3,
                        game.team1.player4, game.team1.player5, game.team1.player6
                    ]:
                        player_stats.cups_made += 1
                        teamA_cup_hitters.append(player)
                    else:
                        player_stats.own_cups += 1

                player_stats.save()

            except User.DoesNotExist:
                continue  # Ignore invalid player IDs
            
        # Check for clutch shots
        if len(teamA_cup_hitters) == 1:
            solo_shooter = teamA_cup_hitters[0]
            solo_shooter_stats = PlayerStats.objects.get(player=solo_shooter, game=game)
            solo_shooter_stats.clutch_cups += 1
            solo_shooter_stats.save()
            
        if len(teamB_cup_hitters) == 1:
            solo_shooter = teamB_cup_hitters[0]
            solo_shooter_stats = PlayerStats.objects.get(player=solo_shooter, game=game)
            solo_shooter_stats.clutch_cups += 1
            solo_shooter_stats.save()
            
        # Check for death cup
        if deathcups:
            for player_id in deathcups:
                try:
                    player = User.objects.get(pk=player_id)
                    player_stats, _ = PlayerStats.objects.get_or_create(player=player, game=game)
                    player_stats.death_cups += 1
                    player_stats.save()
                except User.DoesNotExist:
                    continue
            
        

        # Create a new round record
        new_round = Round.objects.create(
            game=game,
            round_number=next_round_number,
            cups=cups,
            teamA_rack_status=game.teamA_rack_status,
            teamB_rack_status=game.teamB_rack_status
        )

        # Save the updated game state
        game.save()

        # **Use Serializer to Build Response Data**
        serializer = RoundResponseSerializer(new_round)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
