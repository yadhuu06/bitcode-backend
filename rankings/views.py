from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from authentication.models import CustomUser
from .models import Ranking, Season


class UserSeasonalRanking(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user  
        season = Season.objects.get(is_active=True) 

        try:
            user_ranking = Ranking.objects.get(user=user, season=season)
            data = {
                "username": user.username,
                "season": season.name,
                "rating": user_ranking.rating,
                "wins": user_ranking.wins,
                "losses": user_ranking.losses,
                "total_matches": user_ranking.total_matches,
            }
            return Response(data, status=200)
        except Ranking.DoesNotExist:
            return Response(
                {"error": "No ranking found for this user in the current season."},
                status=404,
            )
