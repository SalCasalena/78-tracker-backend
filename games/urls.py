from django.urls import path
from .views import CreateGameView, NewRoundView, GameStateView, AllGamesView, LeaderboardView


urlpatterns = [
    path('start-game', CreateGameView.as_view(), name='new-game'),                  # POST
    path("game/<int:game_id>", GameStateView.as_view(), name="game-state"),         # GET
    path('game/<int:game_id>/round', NewRoundView.as_view(), name='new-round'),     # POST
    path('games/', AllGamesView.as_view(), name='game-list'),                       # GET
    path("leaderboard/", LeaderboardView.as_view(), name="leaderboard"),

]

