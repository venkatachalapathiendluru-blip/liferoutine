from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
import datetime


class Food(models.Model):
    """Stores food items with their nutritional information"""
    
    QUANTITY_UNIT_CHOICES = [
        ('piece', 'Piece(s)'),
        ('gram', 'Gram(s)'),
        ('kg', 'Kilogram(s)'),
        ('ml', 'Milliliter(s)'),
        ('liter', 'Liter(s)'),
        ('cup', 'Cup(s)'),
        ('tablespoon', 'Tablespoon(s)'),
        ('teaspoon', 'Teaspoon(s)'),
        ('bowl', 'Bowl(s)'),
        ('serving', 'Serving(s)'),
    ]
    
    name = models.CharField(max_length=100, unique=True, help_text="Food item name")
    calories_per_unit = models.IntegerField(
        help_text="Calories per standard unit of this food"
    )
    default_unit = models.CharField(
        max_length=20, 
        choices=QUANTITY_UNIT_CHOICES,
        help_text="Default unit for this food"
    )
    protein_per_unit = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Protein per unit (grams)"
    )
    carbs_per_unit = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Carbohydrates per unit (grams)"
    )
    fat_per_unit = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Fat per unit (grams)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.calories_per_unit} cal/{self.default_unit})"
    
    def get_calories_for_quantity(self, quantity, unit):
        """Calculate calories for given quantity and unit"""
        if self.default_unit == unit:
            return int(float(self.calories_per_unit) * float(quantity))
        
        # Add unit conversion logic here if needed in future
        # For now, assume units are the same
        return int(float(self.calories_per_unit) * float(quantity))


class NutritionGoal(models.Model):
    """Stores user nutrition goals for weight management"""
    
    GOAL_TYPE_CHOICES = [
        ('lose', 'Weight Loss'),
        ('maintain', 'Maintain Weight'),
        ('gain', 'Weight Gain'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nutrition_goals')
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES)
    daily_calorie_target = models.IntegerField(
        help_text="Target daily calories for this goal"
    )
    tolerance_calories = models.IntegerField(
        default=100,
        help_text="Acceptable variance from target"
    )
    start_date = models.DateField(help_text="When this goal starts")
    end_date = models.DateField(null=True, blank=True, help_text="When this goal ends (optional)")
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, help_text="Additional notes about this goal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_goal_type_display()} ({self.daily_calorie_target} cal/day)"
    
    def get_status_for_date(self, date):
        """Get goal status for a specific date"""
        try:
            meal_day = MealDay.objects.get(user=self.user, date=date)
            return meal_day.compare_with_goal()
        except MealDay.DoesNotExist:
            return {
                'actual': 0,
                'target': self.daily_calorie_target,
                'difference': -self.daily_calorie_target,
                'percentage_diff': -100.0,
                'goal_type': self.goal_type,
                'is_on_track': False
            }


class Timeline(models.Model):
    """Stores daily routine timeline for each user"""
    
    ACTIVITY_CHOICES = [
        ('wake_up', 'Wake Up'),
        ('water', 'Water'),
        ('walk', 'Walk'),
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('snacks', 'Snacks'),
        ('dinner', 'Dinner'),
        ('sleep_reminder', 'Sleep Reminder'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timelines')
    date = models.DateField(help_text="Date for this timeline")
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    activity_name = models.CharField(max_length=100)
    scheduled_time = models.TimeField(help_text="Scheduled time for this activity")
    offset_minutes = models.IntegerField(help_text="Minutes offset from wake up time")
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date', 'activity_type']
        ordering = ['date', 'scheduled_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.activity_name} at {self.scheduled_time}"
    
    def mark_completed(self):
        """Mark the activity as completed"""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()


class TimelineSettings(models.Model):
    """Stores user preferences for timeline generation"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='timeline_settings')
    
    # Default offsets (can be customized per user)
    wake_up_offset = models.IntegerField(default=0, help_text="Minutes from wake up time")
    water_offset = models.IntegerField(default=5, help_text="Minutes from wake up time")
    walk_offset = models.IntegerField(default=15, help_text="Minutes from wake up time")
    breakfast_offset = models.IntegerField(default=180, help_text="Minutes from wake up time")
    lunch_offset = models.IntegerField(default=420, help_text="Minutes from wake up time")
    snacks_offset = models.IntegerField(default=600, help_text="Minutes from wake up time")
    dinner_offset = models.IntegerField(default=840, help_text="Minutes from wake up time")
    sleep_reminder_offset = models.IntegerField(default=960, help_text="Minutes from wake up time")
    
    # Water settings
    water_amount_ml = models.IntegerField(default=300, help_text="Water amount in ml")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} Timeline Settings"


class MealDay(models.Model):
    """Stores meal planning data for a user for a specific date"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_days')
    date = models.DateField(help_text="Date for this meal plan")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date} Meal Plan"
    
    def get_meal_items(self):
        """Get all meal items for this day"""
        return self.meal_items.all().order_by('meal_type', 'created_at')
    
    def get_meal_by_type(self, meal_type):
        """Get meal items by meal type"""
        return self.meal_items.filter(meal_type=meal_type)
    
    def get_total_calories(self):
        """Calculate total calories for the day"""
        total = 0
        for item in self.meal_items.all():
            total += item.get_calories()
        return total
    
    def get_meal_calories(self, meal_type):
        """Get calories for a specific meal type"""
        total = 0
        for item in self.meal_items.filter(meal_type=meal_type):
            total += item.get_calories()
        return total
    
    def get_calories_breakdown(self):
        """Get calories breakdown by meal type"""
        breakdown = {}
        for meal_type, _ in MealItem.MEAL_TYPE_CHOICES:
            breakdown[meal_type] = self.get_meal_calories(meal_type)
        breakdown['total'] = self.get_total_calories()
        return breakdown
    
    def compare_with_goal(self):
        """Compare daily calories with nutrition goal"""
        try:
            goal = NutritionGoal.objects.get(user=self.user, is_active=True)
            actual = self.get_total_calories()
            target = goal.daily_calorie_target
            
            difference = actual - target
            percentage_diff = (difference / target * 100) if target > 0 else 0
            
            return {
                'actual': actual,
                'target': target,
                'difference': difference,
                'percentage_diff': round(percentage_diff, 1),
                'goal_type': goal.goal_type,
                'is_on_track': abs(difference) <= goal.tolerance_calories
            }
        except NutritionGoal.DoesNotExist:
            return {
                'actual': self.get_total_calories(),
                'target': None,
                'difference': None,
                'percentage_diff': None,
                'goal_type': None,
                'is_on_track': None
            }


class MealItem(models.Model):
    """Stores individual meal items for a meal day"""
    
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('snacks', 'Snacks'),
        ('dinner', 'Dinner'),
    ]
    
    QUANTITY_UNIT_CHOICES = [
        ('piece', 'Piece(s)'),
        ('gram', 'Gram(s)'),
        ('kg', 'Kilogram(s)'),
        ('ml', 'Milliliter(s)'),
        ('liter', 'Liter(s)'),
        ('cup', 'Cup(s)'),
        ('tablespoon', 'Tablespoon(s)'),
        ('teaspoon', 'Teaspoon(s)'),
        ('bowl', 'Bowl(s)'),
        ('serving', 'Serving(s)'),
    ]
    
    meal_day = models.ForeignKey(MealDay, on_delete=models.CASCADE, related_name='meal_items')
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES)
    food = models.ForeignKey(Food, on_delete=models.CASCADE, help_text="Food item")
    food_name = models.CharField(max_length=100, help_text="Food item name (legacy)")
    quantity = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0.1)],
        help_text="Quantity amount"
    )
    quantity_unit = models.CharField(max_length=20, choices=QUANTITY_UNIT_CHOICES)
    calories = models.IntegerField(null=True, blank=True, help_text="Calculated calories")
    notes = models.TextField(blank=True, help_text="Additional notes about this food item")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['meal_type', 'created_at']
    
    def __str__(self):
        food_name = self.food_name if self.food_name else (self.food.name if self.food else "Unknown")
        return f"{food_name} ({self.quantity} {self.get_quantity_unit_display()}) - {self.get_meal_type_display()}"
    
    def calculate_calories(self):
        """Calculate calories for this meal item"""
        if self.food:
            return self.food.get_calories_for_quantity(self.quantity, self.quantity_unit)
        elif self.calories:
            return self.calories
        return 0
    
    def get_calories(self):
        """Get calories for this meal item"""
        if self.food:
            return self.calculate_calories()
        return self.calories or 0
