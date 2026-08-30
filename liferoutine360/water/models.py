from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, time, timedelta
from decimal import Decimal


class WaterGoal(models.Model):
    """Stores user's daily water intake goals"""
    
    WATER_TARGET_CHOICES = [
        (2.0, '2 Liters'),
        (2.5, '2.5 Liters'),
        (3.0, '3 Liters'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='water_goals')
    water_target_liters = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        choices=WATER_TARGET_CHOICES,
        help_text="Daily water intake target in liters"
    )
    start_date = models.DateField(help_text="When this goal starts")
    end_date = models.DateField(null=True, blank=True, help_text="When this goal ends (optional)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.water_target_liters}L/day"
    
    def get_target_ml(self):
        """Convert target to milliliters"""
        return int(float(self.water_target_liters) * 1000)


class WaterSchedule(models.Model):
    """Stores daily water intake schedule with time slots"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='water_schedules')
    date = models.DateField(help_text="Date for this schedule")
    water_goal = models.ForeignKey(WaterGoal, on_delete=models.CASCADE, related_name='schedules')
    wake_up_time = models.TimeField(help_text="User's wake up time for this day")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date} Water Schedule"
    
    def get_time_slots(self):
        """Get all time slots for this schedule"""
        return self.time_slots.all().order_by('scheduled_time')
    
    def get_total_planned(self):
        """Get total planned water intake in ml"""
        return sum(slot.amount_ml for slot in self.time_slots.all())
    
    def get_total_consumed(self):
        """Get total consumed water intake in ml"""
        return sum(slot.get_consumed_amount() for slot in self.time_slots.all())
    
    def get_remaining(self):
        """Get remaining water intake in ml"""
        return self.get_total_planned() - self.get_total_consumed()
    
    def get_completion_percentage(self):
        """Get completion percentage"""
        total_planned = self.get_total_planned()
        if total_planned == 0:
            return 0
        return round((self.get_total_consumed() / total_planned) * 100, 1)


class WaterTimeSlot(models.Model):
    """Individual water intake time slots"""
    
    schedule = models.ForeignKey(WaterSchedule, on_delete=models.CASCADE, related_name='time_slots')
    scheduled_time = models.TimeField(help_text="Scheduled time for water intake")
    amount_ml = models.IntegerField(
        validators=[MinValueValidator(50), MaxValueValidator(1000)],
        help_text="Amount of water in milliliters"
    )
    is_meal_restricted = models.BooleanField(
        default=False,
        help_text="Whether this slot avoids meal times"
    )
    meal_type = models.CharField(
        max_length=20,
        blank=True,
        help_text="Associated meal type if restricted"
    )
    is_consumed = models.BooleanField(default=False)
    consumed_amount_ml = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Actual amount consumed in ml"
    )
    consumed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_time']
    
    def __str__(self):
        return f"{self.scheduled_time.strftime('%I:%M %p')} - {self.amount_ml}ml"
    
    def get_consumed_amount(self):
        """Get consumed amount, defaulting to planned amount if marked as consumed"""
        if self.is_consumed:
            return self.consumed_amount_ml or self.amount_ml
        return 0
    
    def mark_consumed(self, amount_ml=None):
        """Mark this time slot as consumed"""
        self.is_consumed = True
        self.consumed_amount_ml = amount_ml or self.amount_ml
        self.consumed_at = timezone.now()
        self.save()


class WaterIntakeEngine:
    """Engine for generating optimal water intake schedules"""
    
    @staticmethod
    def generate_schedule(user, date, water_goal_liters, wake_up_time, meal_times=None):
        """
        Generate water intake schedule avoiding meal times
        
        Args:
            user: User object
            date: Date for schedule
            water_goal_liters: Target water intake in liters
            wake_up_time: User's wake up time
            meal_times: Dict of meal times {'breakfast': time, 'lunch': time, 'dinner': time}
            
        Returns:
            WaterSchedule object with generated time slots
        """
        
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
    def _get_default_meal_times(wake_up_time):
        """Get default meal times based on wake up time"""
        wake_up_datetime = datetime.combine(datetime.today(), wake_up_time)
        
        return {
            'breakfast': (wake_up_datetime + timedelta(hours=3)).time(),
            'lunch': (wake_up_datetime + timedelta(hours=7)).time(),
            'dinner': (wake_up_datetime + timedelta(hours=12)).time()
        }
    
    @staticmethod
    def _generate_time_slots(water_goal_liters, wake_up_time, meal_times):
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
                'notes': f'Slot {i+1} of {num_slots}'
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
