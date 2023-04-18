# Django Imports
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and
        password.
        """
        if not email:
            raise ValueError("The given email must be set")

        email = UserManager.normalize_email(email)

        user = self.model(
            email=email,
            is_active=True,
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField("email", max_length=255, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.get_full_name() + "  " + self.email


class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)

    @property
    def games(self):
        return (self.host_games.all() | self.guest_games.all())

    @property
    def wins(self):
        return sum([1 for game in self.games if self == game.winner])

    @property
    def loses(self):
        return sum([1 for game in self.games if self == game.loser])

    @property
    def draws(self):
        return len(self.games) - self.wins - self.loses

    def __str__(self):
        return self.name if self.name else str(self.id)


class Game(models.Model):
    host_team = models.ForeignKey(
        Team, related_name="host_games", on_delete=models.CASCADE
    )
    host_team_score = models.PositiveIntegerField()
    guest_team = models.ForeignKey(
        Team, related_name="guest_games", on_delete=models.CASCADE
    )
    guest_team_score = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.host_team} ({self.host_team_score}) - {self.guest_team} ({self.guest_team_score})"

    def is_draw(self):
        return self.host_team_score == self.guest_team_score

    @property
    def winner(self):
        if self.is_draw():
            return None
        return self.host_team if self.host_team_score > self.guest_team_score else self.guest_team

    @property
    def loser(self):
        if self.is_draw():
            return None
        return self.host_team if self.host_team_score < self.guest_team_score else self.guest_team

    def clean(self):
        if self.host_team.name == self.guest_team.name:
            raise ValidationError("Guest and Host teams must not be the same.")
