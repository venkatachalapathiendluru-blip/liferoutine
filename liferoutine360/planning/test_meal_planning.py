from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from planning.models import MealDay, MealItem


class MealPlanningTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_meal_day_creation(self):
        """Test MealDay model creation"""
        meal_day = MealDay.objects.create(
            user=self.user,
            date=date.today()
        )
        
        self.assertEqual(meal_day.user, self.user)
        self.assertEqual(meal_day.date, date.today())
        self.assertEqual(str(meal_day), f"{self.user.username} - {date.today()} Meal Plan")
    
    def test_meal_item_creation(self):
        """Test MealItem model creation"""
        meal_day = MealDay.objects.create(
            user=self.user,
            date=date.today()
        )
        
        meal_item = MealItem.objects.create(
            meal_day=meal_day,
            meal_type='breakfast',
            food='Oatmeal',
            quantity=1,
            quantity_unit='bowl',
            calories=150
        )
        
        self.assertEqual(meal_item.meal_day, meal_day)
        self.assertEqual(meal_item.meal_type, 'breakfast')
        self.assertEqual(meal_item.food, 'Oatmeal')
        self.assertEqual(meal_item.quantity, 1)
        self.assertEqual(meal_item.quantity_unit, 'bowl')
        self.assertEqual(meal_item.calories, 150)
        self.assertEqual(
            str(meal_item), 
            'Oatmeal (1.00 bowl(s)) - Breakfast'
        )
    
    def test_meal_day_unique_constraint(self):
        """Test unique constraint on user and date"""
        MealDay.objects.create(
            user=self.user,
            date=date.today()
        )
        
        # Should not be able to create another MealDay for same user and date
        with self.assertRaises(Exception):
            MealDay.objects.create(
                user=self.user,
                date=date.today()
            )
    
    def test_get_meal_items(self):
        """Test getting meal items for a day"""
        meal_day = MealDay.objects.create(
            user=self.user,
            date=date.today()
        )
        
        # Create multiple meal items
        MealItem.objects.create(
            meal_day=meal_day,
            meal_type='breakfast',
            food='Oatmeal',
            quantity=1,
            quantity_unit='bowl'
        )
        
        MealItem.objects.create(
            meal_day=meal_day,
            meal_type='lunch',
            food='Chicken',
            quantity=100,
            quantity_unit='gram'
        )
        
        items = meal_day.get_meal_items()
        self.assertEqual(items.count(), 2)
    
    def test_get_meal_by_type(self):
        """Test getting meals by type"""
        meal_day = MealDay.objects.create(
            user=self.user,
            date=date.today()
        )
        
        # Create breakfast items
        MealItem.objects.create(
            meal_day=meal_day,
            meal_type='breakfast',
            food='Oatmeal',
            quantity=1,
            quantity_unit='bowl'
        )
        
        MealItem.objects.create(
            meal_day=meal_day,
            meal_type='breakfast',
            food='Banana',
            quantity=1,
            quantity_unit='piece'
        )
        
        # Create lunch item
        MealItem.objects.create(
            meal_day=meal_day,
            meal_type='lunch',
            food='Chicken',
            quantity=100,
            quantity_unit='gram'
        )
        
        breakfast_items = meal_day.get_meal_by_type('breakfast')
        self.assertEqual(breakfast_items.count(), 2)
        
        lunch_items = meal_day.get_meal_by_type('lunch')
        self.assertEqual(lunch_items.count(), 1)