from django.contrib import admin
from .models import Game, Team, Round, PlayerStats


admin.site.register(Game)
admin.site.register(Team)
admin.site.register(Round)
admin.site.register(PlayerStats)