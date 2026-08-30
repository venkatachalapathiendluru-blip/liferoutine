from datetime import datetime, time, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from .models import WaterGoal, WaterSchedule, WaterTimeSlot


class WaterIntakeEngine:
    """Engine for generating optimal water intake schedules"""
    
    @staticmethod
    def generate_schedule(user, date, water_goal_liters, wake_up_time, meal_times=None):
        """
        Generate water intake schedule avoiding meal times
        
        Args:
            user: User object
            date: Date for schedule
            water_goal_liters: Target water intake in liters (2.0, 2.5, or 3.0)
            wake_up_time: User's wake up time
            meal_times: Dict of meal times {'breakfast': time, 'lunch': time, 'dinner': time}
            
        Returns:
            WaterSchedule object with generated time slots
        """
        
        # Validate water goal
        if water_goal_liters not in [2.0, 2.5, 3.0]:
            raise ValueError("Water goal must be 2.0, 2.5, or 3.0 liters")
        
        # Default meal times if not provided
        if meal_times is None:
            meal_times = WaterIntakeEngine._get_default_meal_times(wake_up_time)
        
        # Create water goal and schedule
        water_goal = WaterGoal.objects.create(
            user=user,
            water_target_liters=water_goal_liters,
            start_date=date
        )
        
        schedule = WaterSchedule.objects.create(
            user=user,
            date=date,
            water_goal=water_goal,
            wake_up_time=wake_up_time
        )
        
        # Generate time slots
        time_slots = WaterIntakeEngine._generate_time_slots(
            water_goal_liters, wake_up_time, meal_times
        )
        
        # Create time slot objects
        for slot_data in time_slots:
            WaterTimeSlot.objects.create(
                schedule=schedule,
                scheduled_time=slot_data['time'],
                amount_ml=slot_data['amount_ml'],
                is_meal_restricted=slot_data['is_meal_restricted'],
                meal_type=slot_data.get('meal_type', ''),
                notes=slot_data.get('notes', '')
            )
        
        return schedule
    
    @staticmethod
    def _get_default_meal_times(wake_up_time: time) -> Dict[str, time]:
        """Get default meal times based on wake up time"""
        wake_up_datetime = datetime.combine(datetime.today(), wake_up_time)
        
        return {
            'breakfast': (wake_up_datetime + timedelta(hours=3)).time(),
            'lunch': (wake_up_datetime + timedelta(hours=7)).time(),
            'dinner': (wake_up_datetime + timedelta(hours=12)).time()
        }
    
    @staticmethod
    def _generate_time_slots(water_goal_liters: float, wake_up_time: time, 
                           meal_times: Dict[str, time]) -> List[Dict]:
        """Generate optimal time slots for water intake"""
        
        target_ml = int(float(water_goal_liters) * 1000)
        wake_up_datetime = datetime.combine(datetime.today(), wake_up_time)
        
        # Define restricted periods (30 mins before and after meals)
        restricted_periods = []
        for meal_name, meal_time in meal_times.items():
            meal_datetime = datetime.combine(datetime.today(), meal_time)
            restricted_periods.append({
                'start': meal_datetime - timedelta(minutes=30),
                'end': meal_datetime + timedelta(minutes=30),
                'meal_type': meal_name
            })
        
        # Generate available time slots
        available_slots = []
        current_time = wake_up_datetime
        end_time = wake_up_datetime + timedelta(hours=16)  # 16 hours after wake up
        
        # Generate slots every 30 minutes
        while current_time < end_time:
            slot_time = current_time.time()
            
            # Check if slot is in restricted period
            is_restricted = False
            restricted_meal = None
            
            slot_datetime = datetime.combine(datetime.today(), slot_time)
            
            for period in restricted_periods:
                if period['start'] <= slot_datetime <= period['end']:
                    is_restricted = True
                    restricted_meal = period['meal_type']
                    break
            
            if not is_restricted:
                available_slots.append({
                    'time': slot_time,
                    'datetime': slot_datetime
                })
            
            current_time += timedelta(minutes=30)
        
        # Select 8-10 optimal slots and distribute water
        num_slots = min(max(8, len(available_slots) // 4), 10)
        selected_slots = available_slots[:num_slots]
        
        # Calculate water amount per slot
        base_amount = target_ml // num_slots
        remainder = target_ml % num_slots
        
        time_slots = []
        for i, slot in enumerate(selected_slots):
            amount = base_amount + (1 if i < remainder else 0)
            
            time_slots.append({
                'time': slot['time'],
                'amount_ml': amount,
                'is_meal_restricted': True,
                'meal_type': '',
                'notes': f'Slot {i+1} of {num_slots} - Avoid meal times'
            })
        
        return time_slots
    
    @staticmethod
    def get_or_create_schedule(user, date):
        """Get existing schedule or create new one"""
        try:
            return WaterSchedule.objects.get(user=user, date=date)
        except WaterSchedule.DoesNotExist:
            # Try to get user's water goal and timeline settings
            try:
                water_goal = WaterGoal.objects.filter(user=user, is_active=True).first()
                if not water_goal:
                    # Create default goal
                    water_goal = WaterGoal.objects.create(
                        user=user,
                        water_target_liters=2.5,
                        start_date=date
                    )
                
                # Get wake up time from timeline
                from liferoutine360.planning.models import Timeline
                timeline = Timeline.objects.filter(
                    user=user, 
                    date=date, 
                    activity_type='wake_up'
                ).first()
                
                wake_up_time = timeline.scheduled_time if timeline else time(6, 0)
                
                # Get meal times
                meal_times = {}
                for meal_type in ['breakfast', 'lunch', 'dinner']:
                    meal_timeline = Timeline.objects.filter(
                        user=user,
                        date=date,
                        activity_type=meal_type
                    ).first()
                    if meal_timeline:
                        meal_times[meal_type] = meal_timeline.scheduled_time
                
                return WaterIntakeEngine.generate_schedule(
                    user, date, water_goal.water_target_liters, wake_up_time, meal_times
                )
                
            except Exception as e:
                print(f"Error creating water schedule: {e}")
                return None
    
    @staticmethod
    def get_water_summary(user, date):
        """Get comprehensive water intake summary for a date"""
        try:
            schedule = WaterSchedule.objects.get(user=user, date=date)
            time_slots = schedule.get_time_slots()
            
            return {
                'target_liters': float(schedule.water_goal.water_target_liters),
                'target_ml': schedule.water_goal.get_target_ml(),
                'planned_ml': schedule.get_total_planned(),
                'consumed_ml': schedule.get_total_consumed(),
                'remaining_ml': schedule.get_remaining(),
                'completion_percentage': schedule.get_completion_percentage(),
                'time_slots': [
                    {
                        'time': slot.scheduled_time.strftime('%I:%M %p'),
                        'amount_ml': slot.amount_ml,
                        'is_consumed': slot.is_consumed,
                        'consumed_ml': slot.get_consumed_amount(),
                        'notes': slot.notes
                    }
                    for slot in time_slots
                ]
            }
        except WaterSchedule.DoesNotExist:
            return None
    
    @staticmethod
    def mark_water_consumed(user, date, slot_time, amount_ml=None):
        """Mark a water time slot as consumed"""
        try:
            schedule = WaterSchedule.objects.get(user=user, date=date)
            slot = schedule.time_slots.get(scheduled_time=slot_time)
            slot.mark_consumed(amount_ml)
            return True
        except (WaterSchedule.DoesNotExist, WaterTimeSlot.DoesNotExist):
            return False
    
    @staticmethod
    def update_water_goal(user, water_target_liters, start_date=None):
        """Update user's water goal"""
        if water_target_liters not in [2.0, 2.5, 3.0]:
            raise ValueError("Water goal must be 2.0, 2.5, or 3.0 liters")
        
        # Deactivate existing goals
        WaterGoal.objects.filter(user=user, is_active=True).update(is_active=False)
        
        # Create new goal
        WaterGoal.objects.create(
            user=user,
            water_target_liters=water_target_liters,
            start_date=start_date or datetime.now().date(),
            is_active=True
        )