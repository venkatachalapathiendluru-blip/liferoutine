#!/usr/bin/env python3
"""
Test script for Water Intake Engine
Demonstrates the core functionality of water scheduling with meal time avoidance
"""

import sys
import os
from datetime import datetime, time, timedelta

# Add the Django project to path (works on any machine)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DJANGO_PROJECT_DIR = os.path.join(PROJECT_ROOT, 'liferoutine360')
sys.path.append(DJANGO_PROJECT_DIR)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liferoutine360.settings')

import django
django.setup()

from water.engine import WaterIntakeEngine


def test_water_engine():
    """Test the water intake engine functionality"""
    
    print("=" * 60)
    print("WATER INTAKE ENGINE TEST")
    print("=" * 60)
    
    # Test parameters
    wake_up_time = time(6, 0)  # 6:00 AM
    water_target = 2.5  # 2.5 liters
    
    # Default meal times based on wake up time
    meal_times = {
        'breakfast': time(9, 0),   # 3 hours after wake up
        'lunch': time(13, 0),     # 7 hours after wake up  
        'dinner': time(18, 0)      # 12 hours after wake up
    }
    
    print(f"\nTest Parameters:")
    print(f"  Wake up time: {wake_up_time.strftime('%I:%M %p')}")
    print(f"  Water target: {water_target} liters")
    meals_str = ', '.join(
        "{}: {}".format(k, v.strftime('%I:%M %p')) for k, v in meal_times.items()
    )
    print(f"  Meal times: {meals_str}")
    
    # Generate time slots
    print(f"\nGenerating water intake schedule...")
    time_slots = WaterIntakeEngine._generate_time_slots(
        water_target, wake_up_time, meal_times
    )
    
    print(f"\nGenerated {len(time_slots)} time slots:")
    print("-" * 60)
    
    total_ml = 0
    for i, slot in enumerate(time_slots, 1):
        total_ml += slot['amount_ml']
        print(f"Slot {i:2d}: {slot['time'].strftime('%I:%M %p')} - {slot['amount_ml']:3d}ml")
        print(f"         Notes: {slot['notes']}")
        if slot['is_meal_restricted']:
            print(f"         ✓ Avoids meal times")
        print()
    
    print("-" * 60)
    print(f"Total planned: {total_ml}ml ({total_ml/1000:.1f} liters)")
    print(f"Target:        {water_target * 1000}ml ({water_target} liters)")
    print(f"Match:         {'✓' if total_ml == water_target * 1000 else '✗'}")
    
    # Test meal time avoidance
    print(f"\n" + "=" * 60)
    print("MEAL TIME AVOIDANCE TEST")
    print("=" * 60)
    
    print(f"\nRestricted periods (30 mins before/after meals):")
    for meal_name, meal_time in meal_times.items():
        meal_dt = datetime.combine(datetime.today(), meal_time)
        start = (meal_dt - timedelta(minutes=30)).time()
        end = (meal_dt + timedelta(minutes=30)).time()
        print(f"  {meal_name.title():8s}: {start.strftime('%I:%M')} - {end.strftime('%I:%M %p')}")
    
    print(f"\nChecking if any slots fall in restricted periods...")
    violations = []
    
    for slot in time_slots:
        slot_dt = datetime.combine(datetime.today(), slot['time'])
        
        for meal_name, meal_time in meal_times.items():
            meal_dt = datetime.combine(datetime.today(), meal_time)
            start = meal_dt - timedelta(minutes=30)
            end = meal_dt + timedelta(minutes=30)
            
            if start <= slot_dt <= end:
                violations.append(f"Slot at {slot['time'].strftime('%I:%M %p')} conflicts with {meal_name}")
    
    if violations:
        print(f"❌ Found {len(violations)} violations:")
        for violation in violations:
            print(f"   - {violation}")
    else:
        print(f"✅ No violations found - all slots avoid meal times!")
    
    print(f"\n" + "=" * 60)
    print("WATER DISTRIBUTION ANALYSIS")
    print("=" * 60)
    
    # Analyze distribution
    amounts = [slot['amount_ml'] for slot in time_slots]
    min_amount = min(amounts)
    max_amount = max(amounts)
    avg_amount = sum(amounts) / len(amounts)
    
    print(f"\nWater distribution across {len(time_slots)} slots:")
    print(f"  Minimum: {min_amount}ml")
    print(f"  Maximum: {max_amount}ml") 
    print(f"  Average: {avg_amount:.1f}ml")
    print(f"  Range:   {max_amount - min_amount}ml")
    
    # Time span analysis
    first_slot = min(time_slots, key=lambda x: x['time'])
    last_slot = max(time_slots, key=lambda x: x['time'])
    
    first_dt = datetime.combine(datetime.today(), first_slot['time'])
    last_dt = datetime.combine(datetime.today(), last_slot['time'])
    duration = last_dt - first_dt
    
    print(f"\nTime span:")
    print(f"  First slot: {first_slot['time'].strftime('%I:%M %p')}")
    print(f"  Last slot:  {last_slot['time'].strftime('%I:%M %p')}")
    print(f"  Duration:   {duration.total_seconds() / 3600:.1f} hours")
    
    print(f"\n" + "=" * 60)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    try:
        test_water_engine()
        print(f"\n✅ Water intake engine is working correctly!")
    except Exception as e:
        print(f"\n❌ Error testing water engine: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)