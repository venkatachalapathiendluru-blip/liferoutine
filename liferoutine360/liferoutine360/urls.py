"""
URL configuration for liferoutine360 project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Marketing / public site
    path('', include('marketing.urls')),
    # Product app (gated behind login)
    path('app/', include('web.urls')),
    # Django admin + accounts
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
]
