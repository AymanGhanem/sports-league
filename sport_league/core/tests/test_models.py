# Django Imports
from django.core.exceptions import ValidationError
from django.test import TestCase

# App Imports
from core.models import Team, Game


class TeamAndGameTests(TestCase):
    def setUp(self):
        self.team1 = Team.objects.create(name="Team 1")
        self.team2 = Team.objects.create(name="Team 2")
        self.game1 = Game.objects.create(host_team=self.team1, host_team_score=1, guest_team=self.team2,
                                         guest_team_score=2)
        self.game2 = Game.objects.create(host_team=self.team2, host_team_score=0, guest_team=self.team1,
                                         guest_team_score=0)

    def tearDown(self):
        self.team1.delete()
        self.team2.delete()
        self.game1.delete()
        self.game2.delete()

    def test_team_str(self):
        self.assertEqual(str(self.team1), "Team 1")

    def test_team_games(self):
        actual_games = self.team1.games
        expected_games = [self.game1, self.game2]
        self.assertCountEqual(actual_games, expected_games)

    def test_team_wins(self):
        self.assertEqual(self.team1.wins, 0)
        self.assertEqual(self.team2.wins, 1)

    def test_team_loses(self):
        self.assertEqual(self.team1.loses, 1)
        self.assertEqual(self.team2.loses, 0)

    def test_team_draws(self):
        self.assertEqual(self.team1.draws, 1)
        self.assertEqual(self.team2.draws, 1)

    def test_game_str(self):
        self.assertEqual(str(self.game1), "Team 1 (1) - Team 2 (2)")

    def test_game_is_draw(self):
        self.assertFalse(self.game1.is_draw())
        self.assertTrue(self.game2.is_draw())

    def test_game_winner(self):
        self.assertIsNone(self.game2.winner)
        self.assertEqual(self.game1.winner, self.team2)

    def test_game_loser(self):
        self.assertIsNone(self.game2.loser)
        self.assertEqual(self.game1.loser, self.team1)

    def test_game_clean_method(self):
        with self.assertRaises(ValidationError):
            Game.objects.create(host_team=self.team1, host_team_score=1, guest_team=self.team1,
                                guest_team_score=0).clean()
