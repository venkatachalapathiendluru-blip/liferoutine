from datetime import datetime, date, timedelta
from django.utils import timezone


def get_date_range(plan_type, start_date=None, end_date=None):
    """
    Get date range based on plan type
    Returns: (start_date, end_date)
    """
    today = date.today()
    
    if plan_type == 'tomorrow':
        start_date = today + timedelta(days=1)
        end_date = start_date
    
    elif plan_type == 'next_7_days':
        start_date = today + timedelta(days=1)
        end_date = today + timedelta(days=7)
    
    elif plan_type == 'custom':
        if not start_date or not end_date:
            raise ValueError("Custom range requires both start_date and end_date")
    
    else:
        raise ValueError(f"Invalid plan type: {plan_type}")
    
    return start_date, end_date


def create_meal_plan_template():
    """
    Create a basic meal plan template
    Returns dict with meal types and suggested foods
    """
    return {
        'breakfast': [
            {'food': 'Oatmeal', 'quantity': 1, 'unit': 'bowl'},
            {'food': 'Banana', 'quantity': 1, 'unit': 'piece'},
            {'food': 'Almonds', 'quantity': 10, 'unit': 'piece'}
        ],
        'lunch': [
            {'food': 'Grilled Chicken', 'quantity': 100, 'unit': 'gram'},
            {'food': 'Brown Rice', 'quantity': 1, 'unit': 'bowl'},
            {'food': 'Mixed Vegetables', 'quantity': 1, 'unit': 'bowl'}
        ],
        'snacks': [
            {'food': 'Apple', 'quantity': 1, 'unit': 'piece'},
            {'food': 'Yogurt', 'quantity': 1, 'unit': 'cup'}
        ],
        'dinner': [
            {'food': 'Salmon', 'quantity': 150, 'unit': 'gram'},
            {'food': 'Quinoa', 'quantity': 1, 'unit': 'bowl'},
            {'food': 'Steamed Vegetables', 'quantity': 1, 'unit': 'bowl'}
        ]
    }


def get_veg_meal_plan_template():
    """
    Create a vegetarian meal plan template
    """
    return {
        'breakfast': [
            {'food': 'Oatmeal', 'quantity': 1, 'unit': 'bowl'},
            {'food': 'Banana', 'quantity': 1, 'unit': 'piece'},
            {'food': 'Almonds', 'quantity': 10, 'unit': 'piece'}
        ],
        'lunch': [
            {'food': 'Tofu', 'quantity': 150, 'unit': 'gram'},
            {'food': 'Brown Rice', 'quantity': 1, 'unit': 'bowl'},
            {'food': 'Mixed Vegetables', 'quantity': 1, 'unit': 'bowl'}
        ],
        'snacks': [
            {'food': 'Apple', 'quantity': 1, 'unit': 'piece'},
            {'food': 'Yogurt', 'quantity': 1, 'unit': 'cup'}
        ],
        'dinner': [
            {'food': 'Lentils', 'quantity': 1, 'unit': 'bowl'},
            {'food': 'Quinoa', 'quantity': 1, 'unit': 'bowl'},
            {'food': 'Steamed Vegetables', 'quantity': 1, 'unit': 'bowl'}
        ]
    }


def auto_generate_meal_plan(user, target_date, food_preference='VEG'):
    """
    Auto-generate meal plan for a user on a specific date
    """
    from .models import MealDay, MealItem
    
    # Create meal day
    meal_day, created = MealDay.objects.get_or_create(
        user=user,
        date=target_date
    )
    
    # Clear existing meal items
    MealItem.objects.filter(meal_day=meal_day).delete()
    
    # Get template based on food preference
    if food_preference == 'VEG':
        template = get_veg_meal_plan_template()
    else:
        template = create_meal_plan_template()
    
    # Create meal items
    created_items = []
    for meal_type, items in template.items():
        for item in items:
            meal_item = MealItem.objects.create(
                meal_day=meal_day,
                meal_type=meal_type,
                food=item['food'],
                quantity=item['quantity'],
                quantity_unit=item['unit']
            )
            created_items.append(meal_item)
    
    return created_items


def calculate_daily_calories(meal_day):
    """
    Calculate total calories for a meal day
    """
    total_calories = 0
    for meal_item in meal_day.get_meal_items():
        if meal_item.calories:
            total_calories += meal_item.calories
    return total_calories