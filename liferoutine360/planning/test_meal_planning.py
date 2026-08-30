from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from planning.models import Food, MealDay, MealItem


class MealPlanningTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.oatmeal = Food.objects.create(
            name='Oatmeal',
            calories_per_unit=150,
            default_unit='bowl'
        )
        self.chicken = Food.objects.create(
            name='Chicken',
            calories_per_unit=165,
            default_unit='gram'
        )
        self.banana = Food.objects.create(
            name='Banana',
            calories_per_unit=105,
            default_unit='piece'
        )

    def _create_meal_item(self, meal_day, meal_type, food, quantity, unit):
        return MealItem.objects.create(
            meal_day=meal_day,
            meal_type=meal_type,
            food=food,
            food_name=food.name,
            quantity=quantity,
            quantity_unit=unit
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
        
        meal_item = self._create_meal_item(
            meal_day, 'breakfast', self.oatmeal, 1, 'bowl'
        )
        
        self.assertEqual(meal_item.meal_day, meal_day)
        self.assertEqual(meal_item.meal_type, 'breakfast')
        self.assertEqual(meal_item.food, self.oatmeal)
        self.assertEqual(meal_item.quantity, 1)
        self.assertEqual(meal_item.quantity_unit, 'bowl')
        self.assertEqual(meal_item.calculate_calories(), 150)
        self.assertIn('Oatmeal', str(meal_item))
        self.assertIn('Breakfast', str(meal_item))
    
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
        self._create_meal_item(meal_day, 'breakfast', self.oatmeal, 1, 'bowl')
        self._create_meal_item(meal_day, 'lunch', self.chicken, 100, 'gram')
        
        items = meal_day.get_meal_items()
        self.assertEqual(items.count(), 2)
    
    def test_get_meal_by_type(self):
        """Test getting meals by type"""
        meal_day = MealDay.objects.create(
            user=self.user,
            date=date.today()
        )
        
        # Create breakfast items
        self._create_meal_item(meal_day, 'breakfast', self.oatmeal, 1, 'bowl')
        self._create_meal_item(meal_day, 'breakfast', self.banana, 1, 'piece')
        
        # Create lunch item
        self._create_meal_item(meal_day, 'lunch', self.chicken, 100, 'gram')
        
        breakfast_items = meal_day.get_meal_by_type('breakfast')
        self.assertEqual(breakfast_items.count(), 2)
        
        lunch_items = meal_day.get_meal_by_type('lunch')
        self.assertEqual(lunch_items.count(), 1)