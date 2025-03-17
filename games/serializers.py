from rest_framework import serializers
from .models import Round, Game, PlayerStats

class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = ['id', 'game', 'round_number', 'cups']

class GameStateSerializer(serializers.ModelSerializer):
    player_stats = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = [
            "id", "status", "teamA_rack_status", "teamB_rack_status",
            "teamA_cups_made", "teamB_cups_made",
            "teamA_cups_remaining", "teamB_cups_remaining",
            "cups", "player_stats"
        ]

    def get_player_stats(self, obj):
        """Retrieve player statistics for the game and return as JSON."""
        player_stats = PlayerStats.objects.filter(game=obj)
        return {str(stat.player.pk): PlayerStatsSerializer(stat).data for stat in player_stats}


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
            "death_cups", "clutch_cups"
            ]