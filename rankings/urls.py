from django.urls import path
from . import views 

urlpatterns = [
   path('', views.UserSeasonalRanking.as_view(), name='user_ranking'),

    
    
]