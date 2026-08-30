from django.urls import path
from . import views

app_name = 'nutrition'

urlpatterns = [
    path('', views.nutrition_home, name='home'),
    path('meals/', views.meal_list, name='meal_list'),
    path('meals/create/', views.meal_create, name='meal_create'),
    path('track/', views.nutrition_track, name='track'),
]