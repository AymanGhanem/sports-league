# Django Imports
from django.http import JsonResponse

# App Imports
from core.models import Game, Team
from utils.ranking_utils import FirstStrategy, RankingSystem, get_filtered_games, get_ranked_teams

# 3r Party Imports
from http import HTTPStatus
from json import loads, dumps


class GamesHandler:

    def list_games(request):
        request_body = loads(request.body)
        response = get_filtered_games(
            searchkey=request_body['search']['value'].strip(), start=request_body['start'],
            length=request_body['length'], order_by=request_body['order'][0]
        )
        response['draw'] = request_body['draw']
        return JsonResponse(data=response, status=HTTPStatus.OK)

    def delete_game(request):
        request_body = loads(request.body)
        id = request_body.get('id', None)
        if id:
            game = Game.objects.get(id=id)
            game.delete()
        return JsonResponse(data={}, status=HTTPStatus.OK)

    def edit_game(request):
        request_body = loads(request.body)
        game_id = request_body.get('id')
        if not game_id:
            return JsonResponse({'error': 'Missing game ID'}, status=HTTPStatus.BAD_REQUEST)
        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return JsonResponse({'error': 'Game not found'}, status=HTTPStatus.NOT_FOUND)
        try:
            host_team = Team.objects.get(name=request_body.get('host_team', game.host_team))
            game.host_team = host_team
        except:
            pass
        try:
            guest_team = Team.objects.get(name=request_body.get('guest_team', game.guest_team))
            game.guest_team = guest_team
        except:
            pass
        game.host_team_score = request_body.get('host_team_score', game.host_team_score)
        game.guest_team_score = request_body.get('guest_team_score', game.guest_team_score)
        game.save()
        return JsonResponse({'message': 'Game updated successfully'}, status=HTTPStatus.OK)

    def add_game(request):
        request_body = loads(request.body)
        try:
            host_team, _ = Team.objects.get_or_create(name=request_body.get('host_team'))
        except:
            return JsonResponse({'message': 'Host team error'}, status=HTTPStatus.BAD_REQUEST)
        try:
            guest_team, _ = Team.objects.get_or_create(name=request_body.get('guest_team'))
        except:
            return JsonResponse({'message': 'Guest team error'}, status=HTTPStatus.BAD_REQUEST)
        host_team_score = request_body.get('host_team_score')
        guest_team_score = request_body.get('guest_team_score')
        game = Game.objects.create(host_team=host_team, host_team_score=host_team_score, guest_team=guest_team,
                                   guest_team_score=guest_team_score)
        game.clean()
        game.save()
        return JsonResponse({'message': 'Game updated successfully'}, status=HTTPStatus.OK)

    def get_rankings(request):
        request_body = loads(request.body)
        response = get_ranked_teams(
            searchkey=request_body['search']['value'].strip(), start=request_body['start'],
            length=request_body['length'], order_by=request_body['order'][0]
        )
        return JsonResponse(data=response)


class RankingHandler:
    pass
