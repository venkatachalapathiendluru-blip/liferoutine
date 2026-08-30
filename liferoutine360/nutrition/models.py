from django.db import models


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
