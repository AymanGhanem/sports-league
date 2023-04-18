from django.contrib import admin

from core.models import Game, Team, User

admin.site.register(User)
admin.site.register(Game)
admin.site.register(Team)

