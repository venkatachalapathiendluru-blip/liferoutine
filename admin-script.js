class FoodAdmin {
    constructor() {
        this.foodManager = new FoodManager();
        this.calorieCalculator = new CalorieCalculator(this.foodManager);
        this.currentEditingFood = null;
        this.currentEditingIngredient = null;
        this.mealItems = [];
        this.dailyMeals = {
            breakfast: [],
            lunch: [],
            dinner: [],
            snacks: []
        };
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.renderFoods();
        this.renderIngredients();
        this.populateCategorySelect();
        this.populateCalculatorFoodSelect();
    }
    
    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
        
        // Food management
        document.getElementById('addFoodBtn').addEventListener('click', () => this.openFoodModal());
        document.getElementById('foodForm').addEventListener('submit', (e) => this.handleFoodSubmit(e));
        document.getElementById('foodSearch').addEventListener('input', (e) => this.searchFoods(e.target.value));
        document.getElementById('categoryFilter').addEventListener('change', (e) => this.filterByCategory(e.target.value));
        
        // Ingredient management
        document.getElementById('addIngredientBtn').addEventListener('click', () => this.openIngredientModal());
        document.getElementById('ingredientForm').addEventListener('submit', (e) => this.handleIngredientSubmit(e));
        document.getElementById('ingredientSearch').addEventListener('input', (e) => this.searchIngredients(e.target.value));
        
        // Calculator
        document.getElementById('addToMealBtn').addEventListener('click', () => this.addToMeal());
        
        // Modal close buttons
        document.querySelectorAll('.close, .cancel-btn').forEach(btn => {
            btn.addEventListener('click', () => this.closeModals());
        });
        
        // Click outside modal to close
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModals();
            }
        });
    }
    
    switchTab(tabName) {
        // Update nav buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }
    
    // Food Management
    renderFoods(foods = null) {
        const foodList = document.getElementById('foodList');
        const foodsToRender = foods || this.foodManager.foods;
        
        foodList.innerHTML = foodsToRender.map(food => `
            <div class="food-item">
                <div class="item-header">
                    <div class="item-name">${food.name}</div>
                    <div class="item-category">${food.category}</div>
                </div>
                <div class="item-details">
                    <div>Calories: <span class="calories-info">${food.calculateCalories()}</span> per ${food.unit}</div>
                    <div>Ingredients: ${food.ingredients.length > 0 ? food.ingredients.length : 'Pre-defined'}</div>
                </div>
                <div class="item-actions">
                    <button class="edit-btn" onclick="foodAdmin.editFood('${food.id}')">Edit</button>
                    <button class="delete-btn" onclick="foodAdmin.deleteFood('${food.id}')">Delete</button>
                </div>
            </div>
        `).join('');
    }
    
    openFoodModal(food = null) {
        this.currentEditingFood = food;
        const modal = document.getElementById('foodModal');
        const title = document.getElementById('foodModalTitle');
        const form = document.getElementById('foodForm');
        
        if (food) {
            title.textContent = 'Edit Food';
            document.getElementById('foodName').value = food.name;
            document.getElementById('foodCategory').value = food.category;
            document.getElementById('foodCalories').value = food.calories_per_unit;
            document.getElementById('foodUnit').value = food.unit;
            this.renderFoodIngredients(food.ingredients);
        } else {
            title.textContent = 'Add Food';
            form.reset();
            this.renderFoodIngredients([]);
        }
        
        modal.style.display = 'block';
    }
    
    editFood(id) {
        const food = this.foodManager.getFood(id);
        if (food) {
            this.openFoodModal(food);
        }
    }
    
    deleteFood(id) {
        if (confirm('Are you sure you want to delete this food?')) {
            this.foodManager.deleteFood(id);
            this.renderFoods();
        }
    }
    
    handleFoodSubmit(e) {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('foodName').value,
            category: document.getElementById('foodCategory').value,
            calories_per_unit: parseInt(document.getElementById('foodCalories').value),
            unit: document.getElementById('foodUnit').value
        };
        
        if (this.currentEditingFood) {
            this.foodManager.updateFood(this.currentEditingFood.id, formData);
        } else {
            this.foodManager.addFood(formData.name, formData.category, formData.calories_per_unit, formData.unit);
        }
        
        this.renderFoods();
        this.closeModals();
    }
    
    // Ingredient Management
    renderIngredients(ingredients = null) {
        const ingredientList = document.getElementById('ingredientList');
        const ingredientsToRender = ingredients || this.foodManager.ingredients;
        
        ingredientList.innerHTML = ingredientsToRender.map(ingredient => `
            <div class="ingredient-item">
                <div class="item-header">
                    <div class="item-name">${ingredient.name}</div>
                </div>
                <div class="item-details">
                    <div>Calories: <span class="calories-info">${ingredient.calories_per_unit}</span> per ${ingredient.unit}</div>
                </div>
                <div class="item-actions">
                    <button class="edit-btn" onclick="foodAdmin.editIngredient('${ingredient.id}')">Edit</button>
                    <button class="delete-btn" onclick="foodAdmin.deleteIngredient('${ingredient.id}')">Delete</button>
                </div>
            </div>
        `).join('');
    }
    
    openIngredientModal(ingredient = null) {
        this.currentEditingIngredient = ingredient;
        const modal = document.getElementById('ingredientModal');
        const title = document.getElementById('ingredientModalTitle');
        const form = document.getElementById('ingredientForm');
        
        if (ingredient) {
            title.textContent = 'Edit Ingredient';
            document.getElementById('ingredientName').value = ingredient.name;
            document.getElementById('ingredientCalories').value = ingredient.calories_per_unit;
            document.getElementById('ingredientUnit').value = ingredient.unit;
        } else {
            title.textContent = 'Add Ingredient';
            form.reset();
        }
        
        modal.style.display = 'block';
    }
    
    editIngredient(id) {
        const ingredient = this.foodManager.getIngredient(id);
        if (ingredient) {
            this.openIngredientModal(ingredient);
        }
    }
    
    deleteIngredient(id) {
        if (confirm('Are you sure you want to delete this ingredient?')) {
            this.foodManager.deleteIngredient(id);
            this.renderIngredients();
        }
    }
    
    handleIngredientSubmit(e) {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('ingredientName').value,
            calories_per_unit: parseInt(document.getElementById('ingredientCalories').value),
            unit: document.getElementById('ingredientUnit').value
        };
        
        if (this.currentEditingIngredient) {
            this.foodManager.updateIngredient(this.currentEditingIngredient.id, formData);
        } else {
            this.foodManager.addIngredient(formData.name, formData.calories_per_unit, formData.unit);
        }
        
        this.renderIngredients();
        this.closeModals();
    }
    
    // Search and Filter
    searchFoods(query) {
        if (!query) {
            this.renderFoods();
            return;
        }
        
        const results = this.foodManager.searchFoods(query);
        this.renderFoods(results);
    }
    
    searchIngredients(query) {
        if (!query) {
            this.renderIngredients();
            return;
        }
        
        const results = this.foodManager.ingredients.filter(ingredient => 
            ingredient.name.toLowerCase().includes(query.toLowerCase())
        );
        this.renderIngredients(results);
    }
    
    filterByCategory(category) {
        if (!category) {
            this.renderFoods();
            return;
        }
        
        const results = this.foodManager.getFoodsByCategory(category);
        this.renderFoods(results);
    }
    
    populateCategorySelect() {
        const categorySelect = document.getElementById('foodCategory');
        const categoryFilter = document.getElementById('categoryFilter');
        
        const categories = this.foodManager.categories;
        
        categorySelect.innerHTML = categories.map(cat => 
            `<option value="${cat}">${cat}</option>`
        ).join('');
        
        categoryFilter.innerHTML = '<option value="">All Categories</option>' + 
            categories.map(cat => 
                `<option value="${cat}">${cat}</option>`
            ).join('');
    }
    
    populateCalculatorFoodSelect() {
        const foodSelect = document.getElementById('calculatorFoodSelect');
        
        foodSelect.innerHTML = '<option value="">Select a food</option>' +
            this.foodManager.foods.map(food => 
                `<option value="${food.id}">${food.name} (${food.calculateCalories()} cal/${food.unit})</option>`
            ).join('');
    }
    
    // Calculator Functions
    addToMeal() {
        const foodSelect = document.getElementById('calculatorFoodSelect');
        const quantityInput = document.getElementById('calculatorQuantity');
        
        const foodId = foodSelect.value;
        const quantity = parseFloat(quantityInput.value);
        
        if (!foodId || !quantity) {
            alert('Please select a food and enter quantity');
            return;
        }
        
        const food = this.foodManager.getFood(foodId);
        if (food) {
            this.mealItems.push({
                foodId: foodId,
                quantity: quantity,
                food: food
            });
            
            this.renderMealItems();
            this.updateMealTotal();
            
            // Reset form
            foodSelect.value = '';
            quantityInput.value = '';
        }
    }
    
    renderMealItems() {
        const mealItemsList = document.getElementById('mealItemsList');
        
        mealItemsList.innerHTML = this.mealItems.map((item, index) => `
            <div class="meal-item">
                <span>${item.food.name} - ${item.quantity} ${item.food.unit}</span>
                <span>${Math.round(item.food.calculateCalories() * item.quantity)} cal</span>
                <button class="remove-btn" onclick="foodAdmin.removeFromMeal(${index})">Remove</button>
            </div>
        `).join('');
    }
    
    removeFromMeal(index) {
        this.mealItems.splice(index, 1);
        this.renderMealItems();
        this.updateMealTotal();
    }
    
    updateMealTotal() {
        const total = this.mealItems.reduce((sum, item) => {
            return sum + (item.food.calculateCalories() * item.quantity);
        }, 0);
        
        document.getElementById('mealTotalCalories').textContent = Math.round(total);
    }
    
    // Helper functions
    renderFoodIngredients(ingredients) {
        const container = document.getElementById('foodIngredients');
        
        if (ingredients.length === 0) {
            container.innerHTML = '<div style="color: #999;">No ingredients added</div>';
            return;
        }
        
        container.innerHTML = ingredients.map((item, index) => `
            <div class="ingredient-item">
                <span>${item.ingredient.name} - ${item.quantity} ${item.ingredient.unit}</span>
                <button type="button" class="remove-btn" onclick="foodAdmin.removeIngredientFromFood(${index})">Remove</button>
            </div>
        `).join('');
    }
    
    closeModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
        this.currentEditingFood = null;
        this.currentEditingIngredient = null;
    }
}

// Initialize the admin interface
let foodAdmin;
document.addEventListener('DOMContentLoaded', () => {
    foodAdmin = new FoodAdmin();
});