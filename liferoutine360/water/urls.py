from django.urls import path
from . import views

app_name = 'water'

urlpatterns = [
    path('', views.water_home, name='home'),
    path('track/', views.water_track, name='track'),
    path('history/', views.water_history, name='history'),
    path('settings/', views.water_settings, name='settings'),
    
    # API endpoints
    path('api/summary/<str:target_date>/', views.api_water_summary, name='api_summary'),
    path('api/summary/', views.api_water_summary, name='api_summary_today'),
    path('api/mark-consumed/', views.api_mark_consumed, name='api_mark_consumed'),
    path('api/generate-schedule/', views.api_generate_schedule, name='api_generate_schedule'),
]