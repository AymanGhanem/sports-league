# Django Imports
import csv
import io

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import TestCase

# App Imports
from core.models import User, Team, Game
from utils.csv_utils import process_csv_file
from utils.ranking_utils import RankingSystem, FirstStrategy, search_games_by_searchkey, order_games, get_ranked_teams


class ProcessCsvFileTestCase(TestCase):
    def setUp(self):
        self.url = reverse("core:upload_csv")
        self.user = User.objects.create_user(
            email="testuser@example.com", password="QAZ123ZAQ321?"
        )
        self.team_a = Team.objects.create(name="Team A")
        self.team_b = Team.objects.create(name="Team B")
        self.team_c = Team.objects.create(name="Team C")
        self.team_d = Team.objects.create(name="Team D")

    def test_upload_game_valid_csv(self):
        data = b"Team A,2,Team B,1\nTeam C,3,Team D,1\n"
        file = SimpleUploadedFile("games.csv", data, content_type="text/csv")

        self.client.login(email="testuser@example.com", password="QAZ123ZAQ321?")

        response = self.client.post(self.url, {"csv_file": file})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Game.objects.count(), 2)

    def test_upload_game_invalid_csv(self):
        data = b"Team A,2,Team B\nTeam C,3,Team D,1\n"

        self.client.login(email="testuser@example.com", password="QAZ123ZAQ321?")

        file = SimpleUploadedFile("games.csv", data, content_type="text/csv")

        response = self.client.post(self.url, {"csv_file": file})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Game.objects.count(), 0)

    def test_process_csv_file_valid(self):
        data = b"Team A,2,Team B,1\nTeam C,3,Team D,1\n"
        file = io.BytesIO(data)
        process_csv_file(file)

        game_1 = Game.objects.get(host_team=self.team_a, guest_team=self.team_b)
        game_2 = Game.objects.get(host_team=self.team_c, guest_team=self.team_d)
        self.assertEqual(Game.objects.count(), 2)
        self.assertEqual(game_1.host_team_score, 2)
        self.assertEqual(game_1.guest_team_score, 1)
        self.assertEqual(game_2.host_team_score, 3)
        self.assertEqual(game_2.guest_team_score, 1)


class RankingSystemTestCase(TestCase):
    def setUp(self):
        self.ranking_system = RankingSystem(FirstStrategy())
        self.team1 = Team.objects.create(name="Team 1")
        self.team2 = Team.objects.create(name="Team 2")
        self.team3 = Team.objects.create(name="Team 3")
        self.team4 = Team.objects.create(name="Team 4")

    def tearDown(self):
        Team.objects.all().delete()

    def test_rank_teams(self):
        for team in [self.team1, self.team2, self.team3, self.team4]:
            self.assertEqual(team.wins, 0)
            self.assertEqual(team.draws, 0)
        strategy = FirstStrategy()
        ranking_system = RankingSystem(strategy)
        teams_scores = [self.team1, self.team2, self.team3, self.team4]
        ranked_teams = ranking_system.rank_teams(teams_scores)
        expected_ranking = [
            {'name': 'Team 1', 'points': 0},
            {'name': 'Team 2', 'points': 0},
            {'name': 'Team 3', 'points': 0},
            {'name': 'Team 4', 'points': 0},
        ]
        self.assertEqual(ranked_teams, expected_ranking)

    def test_rank_teams_with_wrong_strategy_type(self):
        with self.assertRaises(TypeError):
            RankingSystem('invalid_strategy')


class TestUtils(TestCase):

    def setUp(self):
        self.team1 = Team.objects.create(name='Team 1')
        self.team2 = Team.objects.create(name='Team 2')
        self.team3 = Team.objects.create(name='Another team')
        self.game1 = Game.objects.create(host_team=self.team1, guest_team=self.team2, host_team_score=1,
                                         guest_team_score=0)
        self.game2 = Game.objects.create(host_team=self.team2, guest_team=self.team3, host_team_score=2,
                                         guest_team_score=2)
        self.game3 = Game.objects.create(host_team=self.team3, guest_team=self.team1, host_team_score=0,
                                         guest_team_score=1)

    def tearDown(self):
        Game.objects.all().delete()
        Team.objects.all().delete()

    def test_search_games_by_searchkey(self):
        searchkey = 'team 1'
        filtered_games = search_games_by_searchkey(Game.objects.all(), searchkey)
        self.assertTrue(all(
            searchkey in game.host_team.name.lower() or searchkey in game.guest_team.name.lower() for game in
            filtered_games))

    def test_order_games(self):
        order_by = {'column': 1, 'dir': 'asc'}
        result = order_games(Game.objects.all(), order_by['column'], order_by['dir'])
        expected_result = [self.game3, self.game1, self.game2]
        self.assertQuerysetEqual(result, expected_result, transform=lambda x: x)
        order_by = {'column': 2, 'dir': 'desc'}
        result = order_games(Game.objects.all(), order_by['column'], order_by['dir'])
        expected_result = [self.game2, self.game1, self.game3]
        self.assertQuerysetEqual(result, expected_result, transform=lambda x: x)


class GetRankedTeamsTestCase(TestCase):
    def setUp(self):
        self.team1 = Team.objects.create(name='Barcelona')
        self.team2 = Team.objects.create(name='Real Madrid')
        self.team3 = Team.objects.create(name='Bayern Munich')
        self.team4 = Team.objects.create(name='Paris Saint-Germain')
        self.team5 = Team.objects.create(name='Manchester United')

    def tearDown(self):
        Team.objects.all().delete()

    def test_get_ranked_teams(self):
        result = get_ranked_teams(searchkey='', start=0, length=5, order_by={'column': 0, 'dir': 'asc'})
        data = result['data']
        self.assertEqual(len(data), 5)
        self.assertEqual(data[0]['name'], self.team1.name)
        self.assertEqual(data[0]['rank'], 1)
        self.assertEqual(data[1]['name'], self.team3.name)
        self.assertEqual(data[1]['rank'], 2)
        self.assertEqual(data[2]['name'], self.team5.name)
        self.assertEqual(data[2]['rank'], 3)
        self.assertEqual(data[3]['name'], self.team4.name)
        self.assertEqual(data[3]['rank'], 4)
        self.assertEqual(data[4]['name'], self.team2.name)
        self.assertEqual(data[4]['rank'], 5)
