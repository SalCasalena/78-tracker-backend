from rest_framework import serializers
from .models import Round, Game

class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = ['id', 'game', 'round_number', 'cups']

class GameStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'status', 'teamA_rack_status', 'teamB_rack_status', 'teamA_cups_made', 'teamB_cups_made', 'teamA_cups_remaining', 'teamB_cups_remaining', 'cups']
