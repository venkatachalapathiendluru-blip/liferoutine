from django.contrib import admin
from .models import Timeline, TimelineSettings, MealDay, MealItem


@admin.register(Timeline)
class TimelineAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'activity_type', 'activity_name', 'scheduled_time', 'is_completed']
    list_filter = ['activity_type', 'is_completed', 'date']
    search_fields = ['user__username', 'activity_name']
    date_hierarchy = 'date'


@admin.register(TimelineSettings)
class TimelineSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'wake_up_offset', 'water_amount_ml']


@admin.register(MealDay)
class MealDayAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'created_at']
    list_filter = ['date']
    search_fields = ['user__username']
    date_hierarchy = 'date'


@admin.register(MealItem)
class MealItemAdmin(admin.ModelAdmin):
    list_display = ['meal_day', 'meal_type', 'food', 'quantity', 'quantity_unit', 'calories']
    list_filter = ['meal_type', 'quantity_unit']
    search_fields = ['food', 'meal_day__user__username']
