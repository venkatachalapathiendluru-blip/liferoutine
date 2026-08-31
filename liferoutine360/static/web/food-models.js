class Ingredient {
    constructor(name, calories_per_unit, unit = 'g') {
        this.id = this.generateId();
        this.name = name;
        this.calories_per_unit = calories_per_unit;
        this.unit = unit;
    }
    
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
    
    toJSON() {
        return {
            id: this.id,
            name: this.name,
            calories_per_unit: this.calories_per_unit,
            unit: this.unit
        };
    }
    
    static fromJSON(data) {
        const ingredient = new Ingredient(data.name, data.calories_per_unit, data.unit);
        ingredient.id = data.id;
        return ingredient;
    }
}

class Food {
    constructor(name, category, calories_per_unit, unit = 'serving', ingredients = []) {
        this.id = this.generateId();
        this.name = name;
        this.category = category;
        this.calories_per_unit = calories_per_unit;
        this.unit = unit;
        this.ingredients = ingredients;
    }
    
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }
    
    addIngredient(ingredient, quantity) {
        this.ingredients.push({
            ingredient: ingredient,
            quantity: quantity
        });
    }
    
    removeIngredient(ingredientId) {
        this.ingredients = this.ingredients.filter(
            item => item.ingredient.id !== ingredientId
        );
    }
    
    calculateCalories() {
        if (this.ingredients.length > 0) {
            return this.ingredients.reduce((total, item) => {
                return total + (item.ingredient.calories_per_unit * item.quantity);
            }, 0);
        }
        return this.calories_per_unit;
    }
    
    toJSON() {
        return {
            id: this.id,
            name: this.name,
            category: this.category,
            calories_per_unit: this.calories_per_unit,
            unit: this.unit,
            ingredients: this.ingredients.map(item => ({
                ingredient: item.ingredient.toJSON(),
                quantity: item.quantity
            }))
        };
    }
    
    static fromJSON(data) {
        const food = new Food(
            data.name,
            data.category,
            data.calories_per_unit,
            data.unit,
            []
        );
        food.id = data.id;
        
        food.ingredients = data.ingredients.map(item => ({
            ingredient: Ingredient.fromJSON(item.ingredient),
            quantity: item.quantity
        }));
        
        return food;
    }
}

class FoodManager {
    constructor() {
        this.foods = [];
        this.ingredients = [];
        this.categories = [
            'Breakfast',
            'Lunch',
            'Dinner',
            'Snacks',
            'Beverages',
            'Desserts',
            'Soups',
            'Salads',
            'Main Course',
            'Side Dish'
        ];
        this.loadData();
    }
    
    addFood(name, category, calories_per_unit, unit = 'serving') {
        const food = new Food(name, category, calories_per_unit, unit);
        this.foods.push(food);
        this.saveData();
        return food;
    }
    
    updateFood(id, updates) {
        const food = this.foods.find(f => f.id === id);
        if (food) {
            Object.assign(food, updates);
            this.saveData();
            return food;
        }
        return null;
    }
    
    deleteFood(id) {
        const index = this.foods.findIndex(f => f.id === id);
        if (index !== -1) {
            const deleted = this.foods.splice(index, 1)[0];
            this.saveData();
            return deleted;
        }
        return null;
    }
    
    addIngredient(name, calories_per_unit, unit = 'g') {
        const ingredient = new Ingredient(name, calories_per_unit, unit);
        this.ingredients.push(ingredient);
        this.saveData();
        return ingredient;
    }
    
    updateIngredient(id, updates) {
        const ingredient = this.ingredients.find(i => i.id === id);
        if (ingredient) {
            Object.assign(ingredient, updates);
            this.saveData();
            return ingredient;
        }
        return null;
    }
    
    deleteIngredient(id) {
        const index = this.ingredients.findIndex(i => i.id === id);
        if (index !== -1) {
            const deleted = this.ingredients.splice(index, 1)[0];
            this.saveData();
            return deleted;
        }
        return null;
    }
    
    getFood(id) {
        return this.foods.find(f => f.id === id);
    }
    
    getIngredient(id) {
        return this.ingredients.find(i => i.id === id);
    }
    
    getFoodsByCategory(category) {
        return this.foods.filter(f => f.category === category);
    }
    
    searchFoods(query) {
        const lowerQuery = query.toLowerCase();
        return this.foods.filter(f => 
            f.name.toLowerCase().includes(lowerQuery) ||
            f.category.toLowerCase().includes(lowerQuery)
        );
    }
    
    saveData() {
        const data = {
            foods: this.foods.map(f => f.toJSON()),
            ingredients: this.ingredients.map(i => i.toJSON())
        };
        localStorage.setItem('foodManagerData', JSON.stringify(data));
    }
    
    loadData() {
        const savedData = localStorage.getItem('foodManagerData');
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                this.foods = data.foods.map(f => Food.fromJSON(f));
                this.ingredients = data.ingredients.map(i => Ingredient.fromJSON(i));
            } catch (error) {
                console.error('Error loading food data:', error);
                this.initializeDefaultData();
            }
        } else {
            this.initializeDefaultData();
        }
    }
    
    initializeDefaultData() {
        // Add default ingredients
        this.addIngredient('Egg', 70, 'large');
        this.addIngredient('Milk', 42, 'cup');
        this.addIngredient('Bread', 80, 'slice');
        this.addIngredient('Chicken Breast', 165, '100g');
        this.addIngredient('Rice', 130, 'cup');
        this.addIngredient('Broccoli', 55, 'cup');
        this.addIngredient('Olive Oil', 120, 'tbsp');
        this.addIngredient('Apple', 95, 'medium');
        this.addIngredient('Banana', 105, 'medium');
        this.addIngredient('Yogurt', 100, 'cup');
        
        // Add default foods
        this.addFood('Scrambled Eggs', 'Breakfast', 140, '2 eggs');
        this.addFood('Toast with Butter', 'Breakfast', 120, '1 slice');
        this.addFood('Grilled Chicken Salad', 'Lunch', 320, '1 serving');
        this.addFood('Rice Bowl', 'Lunch', 280, '1 bowl');
        this.addFood('Apple', 'Snacks', 95, '1 medium');
        this.addFood('Yogurt', 'Snacks', 100, '1 cup');
        this.addFood('Grilled Salmon', 'Dinner', 400, '1 fillet');
        this.addFood('Vegetable Stir-fry', 'Dinner', 250, '1 serving');
    }
}

class CalorieCalculator {
    constructor(foodManager) {
        this.foodManager = foodManager;
    }
    
    calculateMealCalories(mealSelections) {
        let totalCalories = 0;
        const mealDetails = [];
        
        mealSelections.forEach(selection => {
            const food = this.foodManager.getFood(selection.foodId);
            if (food) {
                const calories = food.calculateCalories() * selection.quantity;
                totalCalories += calories;
                
                mealDetails.push({
                    foodName: food.name,
                    quantity: selection.quantity,
                    calories: calories,
                    unit: food.unit
                });
            }
        });
        
        return {
            totalCalories: Math.round(totalCalories),
            details: mealDetails
        };
    }
    
    calculateDailyTotal(dailyMeals) {
        let dailyTotal = 0;
        const mealBreakdown = {};
        
        Object.keys(dailyMeals).forEach(mealType => {
            const mealResult = this.calculateMealCalories(dailyMeals[mealType]);
            dailyTotal += mealResult.totalCalories;
            mealBreakdown[mealType] = mealResult;
        });
        
        return {
            totalCalories: Math.round(dailyTotal),
            mealBreakdown: mealBreakdown
        };
    }
}