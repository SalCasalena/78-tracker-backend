from rest_framework import serializers
from .models import Round, Game, PlayerStats
from users.models import User

class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = ['id', 'game', 'round_number', 'cups']
        
class GameListSerializer(serializers.ModelSerializer):
    team1_name = serializers.CharField(source="team1.team_name")
    team2_name = serializers.CharField(source="team2.team_name")
    date = serializers.DateTimeField(source="created_at" ,format="%Y-%m-%d %H:%M:%S")
    winner = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ["id", "date", "status", "team1_name", "team2_name", "winner"]
    
    def get_winner(self, obj):
        """Safely return the winner's team name or 'TBD' if no winner yet."""
        return obj.winner.team_name if obj.winner else "TBD"


class GameStateSerializer(serializers.ModelSerializer):
    player_stats = serializers.SerializerMethodField()
    winner = serializers.CharField(source="winner.team_name")

    class Meta:
        model = Game
        fields = [
            "id", "status", "teamA_rack_status", "teamB_rack_status",
            "teamA_cups_made", "teamB_cups_made",
            "teamA_cups_remaining", "teamB_cups_remaining",
            "cups", "player_stats", "winner"
        ]

    def get_player_stats(self, obj):
        """Retrieve player statistics grouped by team."""
        # Fetch all player stats for the given game
        player_stats = PlayerStats.objects.filter(game=obj)
        
        # Group players into Team A and Team B
        teamA_players = [
            obj.team1.player1, obj.team1.player2, obj.team1.player3,
            obj.team1.player4, obj.team1.player5, obj.team1.player6
        ]
        teamB_players = [
            obj.team2.player1, obj.team2.player2, obj.team2.player3,
            obj.team2.player4, obj.team2.player5, obj.team2.player6
        ]
        
        # Build the grouped response
        grouped_stats = {
            "teamA": {},
            "teamB": {}
        }

        for stat in player_stats:
            player_id = str(stat.player.pk)
            serialized_data = PlayerStatsSerializer(stat).data

            if stat.player in teamA_players:
                grouped_stats["teamA"][player_id] = serialized_data
            elif stat.player in teamB_players:
                grouped_stats["teamB"][player_id] = serialized_data

        return grouped_stats


class RoundResponseSerializer(serializers.ModelSerializer):
    round_number = serializers.IntegerField()
    cups = serializers.JSONField()
    teamA_cups_made = serializers.IntegerField(source='game.teamA_cups_made')
    teamB_cups_made = serializers.IntegerField(source='game.teamB_cups_made')
    teamA_cups_remaining = serializers.IntegerField(source='game.teamA_cups_remaining')
    teamB_cups_remaining = serializers.IntegerField(source='game.teamB_cups_remaining')
    teamA_rack_status = serializers.CharField(source='game.teamA_rack_status')
    teamB_rack_status = serializers.CharField(source='game.teamB_rack_status')
    player_stats = serializers.SerializerMethodField()

    class Meta:
        model = Round
        fields = [
            "round_number", "cups",
            "teamA_cups_made", "teamB_cups_made",
            "teamA_cups_remaining", "teamB_cups_remaining",
            "teamA_rack_status", "teamB_rack_status",
            "player_stats"
        ]
        
    def get_player_stats(self, obj):
        """Retrieve player statistics for the game."""
        player_stats = PlayerStats.objects.filter(game=obj.game)
        return {str(stat.player.pk): PlayerStatsSerializer(stat).data for stat in player_stats}

class PlayerStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStats
        fields = [
            "shots_taken", "cups_made", 
            "own_cups", "accuracy",
            "death_cups", "clutch_cups",
            "score"
            ]
        
from rest_framework import serializers

class LeaderboardSerializer(serializers.Serializer):  # Use Serializer, not ModelSerializer
    player_name = serializers.CharField()  # Directly provide the player name
    games_played = serializers.IntegerField()
    total_cups_made = serializers.IntegerField()
    average_accuracy = serializers.FloatField()
    total_death_cups = serializers.IntegerField()
    average_rating = serializers.FloatField()

    class Meta:
        model = User
        fields = ["id", "player_name", "games_played", "total_cups_made", "average_accuracy", "total_death_cups", "average_rating"]
