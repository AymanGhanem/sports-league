# Django Imports
from django import forms
from django.contrib.auth.forms import UserCreationForm

from core.models import User, Game, Team


class EventOperation(forms.Form):
    operation = forms.CharField(min_length=5, max_length=75)


class TeamModelForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = "__all__"


class GameModelForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = "__all__"


class GameForm(forms.Form):
    id = forms.IntegerField()
    host_team_id = forms.IntegerField()
    host_team_score = forms.IntegerField()
    guest_team_id = forms.IntegerField()
    guest_team_score = forms.IntegerField()

    def get_host_team_name(self):
        host_team_id = self.cleaned_data.get('host_team_id')
        try:
            host_team = Team.objects.get(id=host_team_id)
            return host_team.name
        except Team.DoesNotExist:
            return None

    def get_guest_team_name(self):
        guest_team_id = self.cleaned_data.get('guest_team_id')
        try:
            guest_team = Team.objects.get(id=guest_team_id)
            return guest_team.name
        except Team.DoesNotExist:
            return None


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError("There is a user with the same email, please choose another email")
