from datetime import datetime, time, timedelta
from typing import List, Dict, Any


def generate_timeline_data(wake_up_time: time = None) -> List[Dict[str, Any]]:
    """
    Generate daily timeline data based on user's wake-up time.
    
    Args:
        wake_up_time: datetime.time object for user's wake up time (defaults to 6:00 AM)
        
    Returns:
        List of dictionaries containing timeline activities
    """
    
    # Use default wake-up time if None is provided
    if wake_up_time is None:
        wake_up_time = time(6, 0)
    
    # Define activities with exact offset requirements from user
    activities = [
        {
            'activity_type': 'wake_up',
            'activity_name': 'Wake Up',
            'offset_minutes': 0,
            'description': 'Start your day with energy and positivity',
            'icon': 'bi-sunrise'
        },
        {
            'activity_type': 'water',
            'activity_name': 'Water Intake',
            'offset_minutes': 5,
            'description': 'Drink 300ml water to hydrate your body',
            'icon': 'bi-droplet',
            'water_amount_ml': 300
        },
        {
            'activity_type': 'walk',
            'activity_name': 'Morning Walk',
            'offset_minutes': 15,
            'description': 'Light walk to freshen up and get some exercise',
            'icon': 'bi-person-walking'
        },
        {
            'activity_type': 'breakfast',
            'activity_name': 'Breakfast',
            'offset_minutes': 180,  # 3 hours
            'description': 'Healthy breakfast to fuel your morning',
            'icon': 'bi-egg-fried'
        },
        {
            'activity_type': 'lunch',
            'activity_name': 'Lunch',
            'offset_minutes': 420,  # 7 hours
            'description': 'Nutritious lunch to maintain energy levels',
            'icon': 'bi-cup-hot'
        },
        {
            'activity_type': 'snacks',
            'activity_name': 'Evening Snacks',
            'offset_minutes': 600,  # 10 hours
            'description': 'Light snacks to keep you going',
            'icon': 'bi-cookie'
        },
        {
            'activity_type': 'dinner',
            'activity_name': 'Dinner',
            'offset_minutes': 840,  # 14 hours
            'description': 'Balanced dinner to end your day',
            'icon': 'bi-moon-stars'
        },
        {
            'activity_type': 'sleep_reminder',
            'activity_name': 'Sleep Reminder',
            'offset_minutes': 960,  # 16 hours
            'description': 'Time to prepare for a good night\'s sleep',
            'icon': 'bi-moon'
        }
    ]
    
    timeline = []
    
    for activity in activities:
        # Ensure wake_up_time is not None
        if wake_up_time is None:
            wake_up_time = time(6, 0)
        
        # Calculate scheduled time
        scheduled_datetime = datetime.combine(datetime.today(), wake_up_time) + timedelta(minutes=activity['offset_minutes'])
        scheduled_time = scheduled_datetime.time()
        
        timeline_item = {
            'activity_type': activity['activity_type'],
            'activity_name': activity['activity_name'],
            'scheduled_time': scheduled_time,
            'offset_minutes': activity['offset_minutes'],
            'description': activity['description'],
            'icon': activity.get('icon', 'bi-circle'),
            'is_completed': False,
            'completed_at': None
        }
        
        # Add water amount if applicable
        if 'water_amount_ml' in activity:
            timeline_item['water_amount_ml'] = activity['water_amount_ml']
            
        timeline.append(timeline_item)
    
    return timeline


def get_activity_descriptions_for_plan(plan: str, food_preference: str) -> Dict[str, str]:
    """
    Get personalized activity descriptions based on user's health plan and food preference.
    
    Args:
        plan: User's health plan (DIABETES, WEIGHT_LOSS, WEIGHT_GAIN)
        food_preference: User's food preference (VEG, NON_VEG)
        
    Returns:
        Dictionary mapping activity_type to personalized description
    """
    
    descriptions = {
        'wake_up': 'Start your day with energy and positivity',
        'water': 'Drink 300ml water to hydrate your body',
        'walk': 'Light walk to freshen up and get some exercise',
        'sleep_reminder': 'Time to prepare for a good night\'s sleep'
    }
    
    # Breakfast descriptions
    if plan == 'DIABETES':
        breakfast_desc = 'Low-glycemic breakfast with complex carbs and protein'
    elif plan == 'WEIGHT_LOSS':
        breakfast_desc = 'Low-calorie, high-protein breakfast for weight management'
    elif plan == 'WEIGHT_GAIN':
        breakfast_desc = 'Nutrient-dense breakfast with healthy calories'
    else:
        breakfast_desc = 'Healthy breakfast to fuel your morning'
    
    if food_preference == 'VEG':
        breakfast_desc += ' (vegetarian options available)'
    else:
        breakfast_desc += ' (both veg and non-veg options available)'
    
    descriptions['breakfast'] = breakfast_desc
    
    # Lunch descriptions
    if plan == 'DIABETES':
        lunch_desc = 'Balanced lunch with controlled carbohydrates'
    elif plan == 'WEIGHT_LOSS':
        lunch_desc = 'Light but filling lunch with lean protein and vegetables'
    elif plan == 'WEIGHT_GAIN':
        lunch_desc = 'Nutrient-rich lunch with adequate protein and healthy fats'
    else:
        lunch_desc = 'Nutritious lunch to maintain energy levels'
        
    descriptions['lunch'] = lunch_desc
    
    # Dinner descriptions
    if plan == 'DIABETES':
        dinner_desc = 'Light dinner with minimal carbs for better glucose control'
    elif plan == 'WEIGHT_LOSS':
        dinner_desc = 'Light, early dinner to support weight loss goals'
    elif plan == 'WEIGHT_GAIN':
        dinner_desc = 'Protein-rich dinner to support muscle growth'
    else:
        dinner_desc = 'Balanced dinner to end your day'
        
    descriptions['dinner'] = dinner_desc
    
    # Snacks description
    if plan == 'DIABETES':
        snacks_desc = 'Low-sugar, high-fiber snacks to maintain stable glucose'
    elif plan == 'WEIGHT_LOSS':
        snacks_desc = 'Low-calorie healthy snacks for energy boost'
    elif plan == 'WEIGHT_GAIN':
        snacks_desc = 'Nutrient-dense snacks for additional calories'
    else:
        snacks_desc = 'Light snacks to keep you going'
        
    descriptions['snacks'] = snacks_desc
    
    return descriptions


# Example usage
if __name__ == "__main__":
    wake_up = time(6, 0)  # 6:00 AM
    timeline = generate_timeline_data(wake_up)
    
    print(f"Generated Timeline (Wake up: {wake_up.strftime('%I:%M %p')})")
    print("-" * 60)
    
    for item in timeline:
        print(f"{item['scheduled_time'].strftime('%I:%M %p'):8s} - {item['activity_name']}")
        print(f"          {item['description']}")
        print()