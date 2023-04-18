# App Imports
from core.models import Team, Game

# 3rd Party 
import csv
import io


def process_csv_file(file_path):
    csv_data = csv.reader(io.TextIOWrapper(file_path, encoding='utf-8'))

    for row in csv_data:
        host_team_name = row[0]
        host_team_score = row[1]
        guest_team_name = row[2]
        guest_team_score = row[3]
        host_team, _ = Team.objects.get_or_create(name=host_team_name)
        guest_team, _ = Team.objects.get_or_create(name=guest_team_name)
        game = Game(
            host_team=host_team,
            host_team_score=host_team_score,
            guest_team=guest_team,
            guest_team_score=guest_team_score
        )
        game.save()
