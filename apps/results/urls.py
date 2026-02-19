from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    path('', views.ResultListView.as_view(), name='list'),
    path('<int:draw_no>/', views.ResultDetailView.as_view(), name='detail'),
]
