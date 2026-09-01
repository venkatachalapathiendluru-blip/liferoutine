from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.meal_planner, name='meal_planner'),
    path('summary/', views.daily_summary, name='daily_summary'),
    path('water/', views.water_tracker, name='water_tracker'),
    path('food-admin/', views.food_admin, name='food_admin'),
]