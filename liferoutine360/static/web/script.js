class MealPlanner {
    constructor() {
        this.foodManager = new FoodManager();
        this.calorieCalculator = new CalorieCalculator(this.foodManager);
        this.waterManager = new WaterIntakeManager();
        this.plannerData = {};
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setDefaultDate();
        this.loadData();
    }
    
    setupEventListeners() {
        const dateRangeSelect = document.getElementById('dateRange');
        const customRange = document.getElementById('customRange');
        const generateBtn = document.getElementById('generateBtn');
        const saveBtn = document.getElementById('saveBtn');
        
        dateRangeSelect.addEventListener('change', (e) => {
            if (e.target.value === 'custom') {
                customRange.style.display = 'flex';
            } else {
                customRange.style.display = 'none';
            }
        });
        
        generateBtn.addEventListener('click', () => this.generatePlanner());
        saveBtn.addEventListener('click', () => this.saveAllData());
        document.getElementById('waterTrackerBtn')?.addEventListener('click', () => this.openWaterTracker());
    }
    
    setDefaultDate() {
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('startDate').value = today;
        document.getElementById('endDate').value = today;
    }
    
    generatePlanner() {
        const startDate = new Date(document.getElementById('startDate').value);
        const dateRange = document.getElementById('dateRange').value;
        let endDate;
        
        if (dateRange === 'custom') {
            endDate = new Date(document.getElementById('endDate').value);
        } else {
            const days = parseInt(dateRange);
            endDate = new Date(startDate);
            endDate.setDate(startDate.getDate() + days - 1);
        }
        
        if (endDate < startDate) {
            alert('End date must be after start date');
            return;
        }
        
        this.renderPlanner(startDate, endDate);
    }
    
    renderPlanner(startDate, endDate) {
        const container = document.getElementById('plannerContainer');
        container.innerHTML = '';
        
        const currentDate = new Date(startDate);
        
        while (currentDate <= endDate) {
            const dayElement = this.createDayElement(currentDate);
            container.appendChild(dayElement);
            currentDate.setDate(currentDate.getDate() + 1);
        }
        
        this.loadDayData();
    }
    
    createDayElement(date) {
        const dayDiv = document.createElement('div');
        dayDiv.className = 'day-planner';
        dayDiv.dataset.date = this.formatDate(date);
        
        const dateStr = date.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        
        dayDiv.innerHTML = `
            <div class="day-header">
                <span>${dateStr}</span>
                <div class="header-right">
                    <span class="daily-calories" id="calories-${this.formatDate(date)}">0 cal</span>
                    <span class="save-indicator" id="save-${this.formatDate(date)}">Saved</span>
                </div>
            </div>
        `;
        
        const meals = ['Early Morning', 'Breakfast', 'Lunch', 'Snacks', 'Dinner'];
        
        meals.forEach(meal => {
            const mealSection = this.createMealSection(meal, this.formatDate(date));
            dayDiv.appendChild(mealSection);
        });
        
        // Add water section for the day
        const waterSection = this.createWaterSection(this.formatDate(date));
        dayDiv.appendChild(waterSection);
        
        return dayDiv;
    }
    
    createMealSection(meal, date) {
        const sectionDiv = document.createElement('div');
        sectionDiv.className = 'meal-section';
        
        const mealClass = meal.toLowerCase().replace(' ', '-');
        
        sectionDiv.innerHTML = `
            <div class="meal-header ${mealClass}">
                ${meal}
                <span class="meal-calories" id="meal-calories-${date}-${meal}">0 cal</span>
            </div>
            <div class="food-options" id="${date}-${meal}">
                ${this.createFoodOptions(meal, date)}
            </div>
        `;
        
        return sectionDiv;
    }
    
    createWaterSection(date) {
        const sectionDiv = document.createElement('div');
        sectionDiv.className = 'meal-section water-section';
        
        sectionDiv.innerHTML = `
            <div class="meal-header water-header">
                💧 Water Intake
                <span class="water-progress" id="water-progress-${date}">0 ml</span>
                <button class="water-log-btn" onclick="mealPlanner.openWaterTracker()">Track Water</button>
            </div>
            <div class="water-info" id="water-info-${date}">
                <p>Click "Track Water" to manage your daily water intake</p>
            </div>
        `;
        
        // Load water progress if available
        setTimeout(() => {
            this.updateWaterProgress(date);
        }, 100);
        
        return sectionDiv;
    }
    
    createFoodOptions(meal, date) {
        const foods = this.getFoodsForMeal(meal);
        return foods.map(food => `
            <div class="food-item">
                <input type="checkbox" 
                       id="${date}-${meal}-${food.id}" 
                       data-date="${date}" 
                       data-meal="${meal}" 
                       data-food-id="${food.id}">
                <label for="${date}-${meal}-${food.id}">
                    ${food.name} 
                    <span class="calorie-info">(${food.calculateCalories()} cal/${food.unit})</span>
                </label>
            </div>
        `).join('');
    }
    
    getFoodsForMeal(meal) {
        // Map meal types to food categories
        const mealToCategory = {
            'Early Morning': ['Beverages', 'Breakfast'],
            'Breakfast': ['Breakfast'],
            'Lunch': ['Lunch', 'Main Course', 'Salads', 'Soups'],
            'Snacks': ['Snacks'],
            'Dinner': ['Dinner', 'Main Course', 'Side Dish']
        };
        
        const categories = mealToCategory[meal] || [];
        return this.foodManager.foods.filter(food => 
            categories.includes(food.category)
        );
    }
    
    formatDate(date) {
        return date.toISOString().split('T')[0];
    }
    
    saveAllData() {
        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
        
        checkboxes.forEach(checkbox => {
            const date = checkbox.dataset.date;
            const meal = checkbox.dataset.meal;
            const foodId = checkbox.dataset.foodId;
            
            if (!this.plannerData[date]) {
                this.plannerData[date] = {};
            }
            
            if (!this.plannerData[date][meal]) {
                this.plannerData[date][meal] = [];
            }
            
            if (checkbox.checked) {
                if (!this.plannerData[date][meal].includes(foodId)) {
                    this.plannerData[date][meal].push(foodId);
                }
            } else {
                this.plannerData[date][meal] = this.plannerData[date][meal].filter(id => id !== foodId);
            }
        });
        
        localStorage.setItem('mealPlannerData', JSON.stringify(this.plannerData));
        this.updateAllCalorieDisplays();
        this.showSaveIndicators();
    }
    
    showSaveIndicators() {
        const dates = Object.keys(this.plannerData);
        
        dates.forEach(date => {
            const indicator = document.getElementById(`save-${date}`);
            if (indicator) {
                indicator.classList.add('show');
                setTimeout(() => {
                    indicator.classList.remove('show');
                }, 2000);
            }
        });
    }
    
    loadData() {
        const savedData = localStorage.getItem('mealPlannerData');
        if (savedData) {
            this.plannerData = JSON.parse(savedData);
        }
    }
    
    loadDayData() {
        Object.keys(this.plannerData).forEach(date => {
            const dayData = this.plannerData[date];
            
            Object.keys(dayData).forEach(meal => {
                const selectedFoodIds = dayData[meal];
                
                selectedFoodIds.forEach(foodId => {
                    const checkbox = document.querySelector(
                        `input[data-date="${date}"][data-meal="${meal}"][data-food-id="${foodId}"]`
                    );
                    
                    if (checkbox) {
                        checkbox.checked = true;
                        checkbox.parentElement.classList.add('selected');
                    }
                });
            });
        });
        
        // Add event listeners to checkboxes for visual feedback and calorie updates
        document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const foodItem = e.target.parentElement;
                if (e.target.checked) {
                    foodItem.classList.add('selected');
                } else {
                    foodItem.classList.remove('selected');
                }
                
                // Update calorie displays
                this.updateMealCalories(e.target.dataset.date, e.target.dataset.meal);
                this.updateDailyCalories(e.target.dataset.date);
            });
        });
        
        // Update all calorie displays after loading data
        this.updateAllCalorieDisplays();
    }
    
    updateMealCalories(date, meal) {
        const checkboxes = document.querySelectorAll(
            `input[data-date="${date}"][data-meal="${meal}"]:checked`
        );
        
        let totalCalories = 0;
        checkboxes.forEach(checkbox => {
            const foodId = checkbox.dataset.foodId;
            const food = this.foodManager.getFood(foodId);
            if (food) {
                totalCalories += food.calculateCalories();
            }
        });
        
        const mealCaloriesElement = document.getElementById(`meal-calories-${date}-${meal}`);
        if (mealCaloriesElement) {
            mealCaloriesElement.textContent = `${totalCalories} cal`;
        }
        
        return totalCalories;
    }
    
    updateDailyCalories(date) {
        const meals = ['Early Morning', 'Breakfast', 'Lunch', 'Snacks', 'Dinner'];
        let dailyTotal = 0;
        
        meals.forEach(meal => {
            dailyTotal += this.updateMealCalories(date, meal);
        });
        
        const dailyCaloriesElement = document.getElementById(`calories-${date}`);
        if (dailyCaloriesElement) {
            dailyCaloriesElement.textContent = `${dailyTotal} cal`;
        }
        
        return dailyTotal;
    }
    
    updateAllCalorieDisplays() {
        const dates = Object.keys(this.plannerData);
        
        dates.forEach(date => {
            this.updateDailyCalories(date);
            this.updateWaterProgress(date);
        });
    }
    
    updateWaterProgress(date) {
        const progress = this.waterManager.getWaterProgress(date);
        const waterProgressElement = document.getElementById(`water-progress-${date}`);
        const waterInfoElement = document.getElementById(`water-info-${date}`);
        
        if (waterProgressElement) {
            waterProgressElement.textContent = `${progress.consumed} / ${progress.target} ml`;
        }
        
        if (waterInfoElement) {
            const percentage = progress.target > 0 ? Math.round((progress.consumed / progress.target) * 100) : 0;
            waterInfoElement.innerHTML = `
                <div class="water-stats">
                    <div class="water-stat">
                        <span class="water-label">Progress:</span>
                        <span class="water-value">${percentage}%</span>
                    </div>
                    <div class="water-stat">
                        <span class="water-label">Remaining:</span>
                        <span class="water-value">${progress.remaining} ml</span>
                    </div>
                </div>
            `;
        }
    }
    
    openWaterTracker() {
        // Open water tracker in a new window/tab
        window.open('/water/', '_blank');
    }
}

// Initialize the meal planner when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MealPlanner();
});