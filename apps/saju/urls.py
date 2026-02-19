from django.urls import path
from . import views

app_name = 'saju'

urlpatterns = [
    path('', views.SajuPageView.as_view(), name='index'),
    path('api/interpret/', views.SajuInterpretAPIView.as_view(), name='interpret'),
]
