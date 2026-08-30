from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'water_target_liters', 'food_preference', 'role', 'wake_up_time', 'sleep_time']
    list_filter = ['plan', 'food_preference', 'role']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
