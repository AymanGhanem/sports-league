# Django Imports 
from django.db.models import Q, Count
from django.core.paginator import Paginator

# Project Imports
from abc import ABC, abstractmethod
import math
from core.forms import GameForm

# App Imports
from core.models import Game, Team


class ScoreStrategy(ABC):
    @abstractmethod
    def rank_teams(self, teams):
        pass


class FirstStrategy(ScoreStrategy):
    def rank_teams(self, teams):
        teams_scores = []
        for team in teams:
            score = team.wins * 3 + team.draws
            teams_scores.append({'name': team.name, 'points': score})
        teams_scores.sort(key=lambda team: (-team['points'], team['name']))
        return teams_scores


class RankingSystem:
    def __init__(self, strategy):
        if not isinstance(strategy, ScoreStrategy):
            raise TypeError("Strategy must be a subclass of ScoreStrategy.")
        self.strategy = strategy

    def rank_teams(self, team_scores):
        return self.strategy.rank_teams(team_scores)


def search_games_by_searchkey(query, searchkey):
    return query.filter(Q(host_team__name__icontains=searchkey) | Q(guest_team__name__icontains=searchkey))


def order_games(query, column_index, dir):
    column_mappings = {
        0: 'id',
        1: 'host_team__name',
        2: 'host_team_score',
        3: 'guest_team__name',
        4: 'guest_team_score',
    }
    direction_mappings = {'asc': "", 'desc': "-"}
    return query.order_by(direction_mappings[dir] + column_mappings[column_index])


def get_filtered_games(searchkey, start, length, order_by):
    games = Game.objects.all()
    total = games.aggregate(Count("id"))["id__count"]
    filtered_games_by_search_key = search_games_by_searchkey(query=games, searchkey=searchkey)
    filtered_ordered_games = order_games(query=filtered_games_by_search_key, column_index=order_by['column'],
                                         dir=order_by['dir'])
    paginator = Paginator(filtered_ordered_games, length)
    paginated_games = paginator.page(math.ceil((start + 1) / length)).object_list
    resulted_games = []
    for game in paginated_games:
        game_form = GameForm(game.__dict__)
        if game_form.is_valid():
            game_data = game_form.cleaned_data
            game_data['host_team_id'] = game_form.get_host_team_name()
            game_data['guest_team_id'] = game_form.get_guest_team_name()
            resulted_games.append(game_data)
    return {'data': resulted_games, 'recordsFiltered': paginator.count, 'recordsTotal': total}


def search_teams_by_searchkey(teams_list, searchkey):
    return [team for team in teams_list if searchkey.lower() in team["name"].lower()]


def order_teams_by_rank(teams_list, direction):
    if direction == "desc":
        teams_list.reverse()
    return teams_list


def get_ranked_teams(searchkey, start, length, order_by):
    teams = Team.objects.all()
    total = teams.aggregate(Count("id"))["id__count"]
    strategy = FirstStrategy()
    ranker = RankingSystem(strategy)
    sorted_teams = ranker.rank_teams(teams)
    for index, team in enumerate(sorted_teams):
        team['rank'] = index + 1
    filtered_ranks_by_search_key = search_teams_by_searchkey(teams_list=sorted_teams, searchkey=searchkey)
    filtered_ordered_teams = order_teams_by_rank(teams_list=filtered_ranks_by_search_key, direction=order_by['dir'])
    filtered_total = len(filtered_ordered_teams)
    if start + length < total:
        filtered_ordered_paginated_teams = filtered_ordered_teams[start: (start + length)]
    else:
        filtered_ordered_paginated_teams = filtered_ordered_teams[start:]
    return {'data': filtered_ordered_paginated_teams, 'recordsFiltered': filtered_total, 'recordsTotal': total}
