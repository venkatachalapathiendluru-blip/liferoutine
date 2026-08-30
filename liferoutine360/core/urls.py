from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('home/', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard_page'),
    path('modules/', views.module_list, name='module_list'),
    path('modules/toggle/<int:module_id>/', views.toggle_module, name='toggle_module'),
    path('modules/create/', views.create_module, name='create_module'),
]