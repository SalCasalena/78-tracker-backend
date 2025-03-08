from django.urls import path
from .views import CreateGameView

urlpatterns = [
    path('start-game', CreateGameView.as_view(), name='start-game'),
    
]
