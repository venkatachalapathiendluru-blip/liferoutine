#!/usr/bin/env python3
"""
Test script for the timeline engine functionality
"""

import os
import sys
import django
from datetime import time, date

# Add the Django project to path (works on any machine)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DJANGO_PROJECT_DIR = os.path.join(PROJECT_ROOT, 'liferoutine360')
sys.path.append(DJANGO_PROJECT_DIR)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liferoutine360.settings')
try:
    django.setup()
except Exception as e:
    print(f"Django setup error: {e}")
    sys.exit(1)

from routine_engine import generate_timeline_data, get_activity_descriptions_for_plan

def test_timeline_generation():
    """Test the timeline generation logic"""
    
    print("Testing Timeline Engine")
    print("=" * 50)
    
    # Test with wake-up time at 6:00 AM
    wake_up_time = time(6, 0)
    
    try:
        timeline = generate_timeline_data(wake_up_time)
        
        print(f"✓ Generated timeline for {wake_up_time.strftime('%I:%M %p')}")
        print(f"✓ Number of activities: {len(timeline)}")
        print()
        
        # Display timeline
        print("Generated Timeline:")
        print("-" * 40)
        
        for item in timeline:
            print(f"{item['scheduled_time'].strftime('%I:%M %p'):8s} - {item['activity_name']}")
            print(f"          Type: {item['activity_type']}")
            print(f"          Offset: {item['offset_minutes']} minutes")
            print(f"          Description: {item['description']}")
            print()
        
        # Test activity descriptions for different plans
        print("Testing Activity Descriptions:")
        print("-" * 40)
        
        plans = ['DIABETES', 'WEIGHT_LOSS', 'WEIGHT_GAIN']
        food_prefs = ['VEG', 'NON_VEG']
        
        for plan in plans:
            for food_pref in food_prefs:
                descriptions = get_activity_descriptions_for_plan(plan, food_pref)
                print(f"{plan} + {food_pref}:")
                print(f"  Breakfast: {descriptions['breakfast']}")
                print(f"  Lunch: {descriptions['lunch']}")
                print(f"  Dinner: {descriptions['dinner']}")
                print()
        
        print("✓ All tests passed!")
        
    except Exception as e:
        print(f"✗ Error in timeline generation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_timeline_generation()
    sys.exit(0 if success else 1)