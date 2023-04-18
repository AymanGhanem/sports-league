# Django Import
from django.test import TestCase

# App Import
from core.models import User, Game, Team
from core.forms import EventOperation, TeamModelForm, GameForm, GameModelForm


class FormsTestCase(TestCase):
    def setUp(self):
        self.team_data = {'name': 'Test Team'}
        self.game_data = {
            'host_team_id': 1,
            'host_team_score': 2,
            'guest_team_id': 2,
            'guest_team_score': 1
        }

    def tearDown(self):
        Team.objects.all().delete()
        Game.objects.all().delete()

    def test_get_host_team_name(self):
        team = Team.objects.create(name='Test Team')
        form_data = {
            'id': 1,
            'host_team_id': team.id,
            'host_team_score': 2,
            'guest_team_id': 2,
            'guest_team_score': 1
        }
        form = GameForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_host_team_name(), team.name)

    def test_get_guest_team_name(self):
        team = Team.objects.create(name='Test Team')
        form_data = {
            'id': 1,
            'host_team_id': 1,
            'host_team_score': 2,
            'guest_team_id': team.id,
            'guest_team_score': 1
        }
        form = GameForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_guest_team_name(), team.name)

    def test_create_team(self):
        form_data = {'name': 'Test Team'}
        form = TeamModelForm(data=form_data)
        self.assertTrue(form.is_valid())
        team = form.save()
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(team.name, 'Test Team')

    def test_event_operation(self):
        form_data = {'operation': 'Test Operation'}
        form = EventOperation(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['operation'], 'Test Operation')
