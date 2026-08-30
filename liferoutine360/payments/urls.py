from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payments_home, name='home'),
    path('subscriptions/', views.subscription_list, name='subscription_list'),
    path('billing/', views.billing_view, name='billing'),
]