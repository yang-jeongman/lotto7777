from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.LandingPageView.as_view(), name='index'),
    path('api/number/<int:number>/stats/', views.NumberDetailAPIView.as_view(), name='number_stats'),
    path('recommendations/', views.MoreRecommendationsView.as_view(), name='more_recommendations'),
]
