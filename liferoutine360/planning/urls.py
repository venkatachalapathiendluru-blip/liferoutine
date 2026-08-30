from django.urls import path
from . import views

app_name = 'planning'

urlpatterns = [
    path('', views.planning_home, name='home'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    
    # Timeline API endpoints
    path('api/timeline/', views.timeline_api, name='timeline_api'),
    path('api/complete/<int:activity_id>/', views.complete_activity, name='complete_activity'),
    path('api/uncomplete/<int:activity_id>/', views.uncomplete_activity, name='uncomplete_activity'),
    
    # Meal planning endpoints
    path('meals/', views.meal_planner_home, name='meal_planner_home'),
    path('api/meals/', views.meal_planner_api, name='meal_planner_api'),
    path('api/meals/auto-generate/', views.auto_generate_meal_plan_api, name='auto_generate_meal_plan_api'),
    
    # Calorie tracking endpoints
    path('api/calories/', views.calorie_tracking_api, name='calorie_tracking_api'),
]