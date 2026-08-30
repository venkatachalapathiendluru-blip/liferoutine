class DailySummary {
    constructor() {
        this.foodManager = new FoodManager();
        this.waterManager = new WaterIntakeManager();
        this.currentDate = new Date().toISOString().split('T')[0];
        this.plannerData = {};
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setDefaultDate();
        this.loadPlannerData();
        this.generateSummary();
    }
    
    setupEventListeners() {
        document.getElementById('summaryDate').addEventListener('change', (e) => {
            this.currentDate = e.target.value;
            this.generateSummary();
        });
        
        document.getElementById('refreshSummary').addEventListener('click', () => {
            this.generateSummary();
        });
        
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });
        
        document.getElementById('shareSummary').addEventListener('click', () => this.shareSummary());
    }
    
    setDefaultDate() {
        document.getElementById('summaryDate').value = this.currentDate;
    }
    
    loadPlannerData() {
        const savedData = localStorage.getItem('mealPlannerData');
        if (savedData) {
            try {
                this.plannerData = JSON.parse(savedData);
            } catch (error) {
                console.error('Error loading planner data:', error);
                this.plannerData = {};
            }
        }
    }
    
    generateSummary() {
        this.updateOverallScore();
        this.updateActivitiesSummary();
        this.updateWaterSummary();
        this.updateCaloriesSummary();
        this.generateHealthMessage();
        this.updateDetailedBreakdowns();
        this.generateRecommendations();
    }
    
    updateOverallScore() {
        const activitiesScore = this.calculateActivitiesScore();
        const waterScore = this.calculateWaterScore();
        const nutritionScore = this.calculateNutritionScore();
        
        const overallScore = Math.round((activitiesScore + waterScore + nutritionScore) / 3);
        
        // Update score circle
        document.getElementById('scoreNumber').textContent = `${overallScore}%`;
        
        // Update score label and color based on performance category
        const scoreLabel = document.getElementById('scoreLabel');
        const scoreCircle = document.getElementById('scoreCircle');
        
        if (overallScore >= 90) {
            scoreLabel.textContent = 'Excellent 🌟';
            scoreCircle.className = 'score-circle bg-success text-white';
        } else if (overallScore >= 75) {
            scoreLabel.textContent = 'Good 👏';
            scoreCircle.className = 'score-circle bg-info text-white';
        } else if (overallScore >= 60) {
            scoreLabel.textContent = 'Improve 📈';
            scoreCircle.className = 'score-circle bg-warning text-white';
        } else {
            scoreLabel.textContent = 'Needs Attention 🎯';
            scoreCircle.className = 'score-circle bg-danger text-white';
        }
        
        // Rotate score circle based on percentage
        const rotation = (overallScore / 100) * 360 - 90;
        scoreCircle.style.transform = `rotate(${rotation}deg)`;
    }
    
    calculateActivitiesScore() {
        const dayData = this.plannerData[this.currentDate];
        if (!dayData) return 0;
        
        let plannedCount = 0;
        let completedCount = 0;
        
        // Count planned activities (all meal slots count as planned)
        const mealTypes = ['breakfast', 'lunch', 'dinner', 'snacks'];
        mealTypes.forEach(meal => {
            plannedCount += 1; // Each meal type is a planned activity
            if (dayData[meal] && dayData[meal].length > 0) {
                completedCount += 1; // Meal is completed if items are selected
            }
        });
        
        // Add water tracking as an activity
        plannedCount += 1;
        const waterProgress = this.waterManager.getWaterProgress(this.currentDate);
        if (waterProgress.percentage >= 80) {
            completedCount += 1;
        }
        
        return plannedCount > 0 ? Math.round((completedCount / plannedCount) * 100) : 0;
    }
    
    calculateWaterScore() {
        const progress = this.waterManager.getWaterProgress(this.currentDate);
        return Math.round((progress.consumed / progress.target) * 100);
    }
    
    calculateNutritionScore() {
        const totalCalories = this.getTotalCalories();
        
        if (totalCalories === 0) return 0;
        if (totalCalories >= 1800 && totalCalories <= 2200) return 100;
        if (totalCalories >= 1600 && totalCalories <= 2400) return 80;
        if (totalCalories >= 1400 && totalCalories <= 2600) return 60;
        if (totalCalories >= 1200 && totalCalories <= 2800) return 40;
        return 20;
    }
    
    updateActivitiesSummary() {
        const dayData = this.plannerData[this.currentDate];
        const activitiesList = document.getElementById('activityList');
        const plannedElement = document.getElementById('plannedActivities');
        const completedElement = document.getElementById('completedActivities');
        const scoreElement = document.getElementById('activitiesScore');
        
        // Calculate activities differently - meal completion as activities
        let plannedCount = 4; // breakfast, lunch, dinner, snacks
        let completedCount = 0;
        let activityHTML = '';
        
        const mealTypes = ['breakfast', 'lunch', 'dinner', 'snacks'];
        mealTypes.forEach(meal => {
            const isCompleted = dayData && dayData[meal] && dayData[meal].length > 0;
            if (isCompleted) {
                completedCount += 1;
                const totalCalories = dayData[meal].reduce((sum, foodId) => {
                    const food = this.foodManager.getFood(foodId);
                    return sum + (food ? food.calculateCalories() : 0);
                }, 0);
                
                activityHTML += `
                    <div class="activity-item completed">
                        <span><i class="bi bi-check-circle-fill text-success me-1"></i>${meal.charAt(0).toUpperCase() + meal.slice(1)}</span>
                        <span>${totalCalories} cal</span>
                    </div>
                `;
            } else {
                activityHTML += `
                    <div class="activity-item missed">
                        <span><i class="bi bi-circle text-muted me-1"></i>${meal.charAt(0).toUpperCase() + meal.slice(1)}</span>
                        <span>Not logged</span>
                    </div>
                `;
            }
        });
        
        // Add water tracking activity
        const waterProgress = this.waterManager.getWaterProgress(this.currentDate);
        plannedCount += 1;
        if (waterProgress.percentage >= 80) {
            completedCount += 1;
            activityHTML += `
                <div class="activity-item completed">
                    <span><i class="bi bi-droplet-fill text-info me-1"></i>Hydration</span>
                    <span>${waterProgress.percentage}%</span>
                </div>
            `;
        } else {
            activityHTML += `
                <div class="activity-item missed">
                    <span><i class="bi bi-droplet text-muted me-1"></i>Hydration</span>
                    <span>${waterProgress.percentage}%</span>
                </div>
            `;
        }
        
        plannedElement.textContent = plannedCount;
        completedElement.textContent = completedCount;
        
        const score = plannedCount > 0 ? Math.round((completedCount / plannedCount) * 100) : 0;
        scoreElement.textContent = `${score}%`;
        
        activitiesList.innerHTML = activityHTML || '<p class="no-data">No activities recorded</p>';
    }
    
    updateWaterSummary() {
        const progress = this.waterManager.getWaterProgress(this.currentDate);
        
        document.getElementById('waterTarget').textContent = `${progress.target} ml`;
        document.getElementById('waterConsumed').textContent = `${progress.consumed} ml`;
        document.getElementById('waterRemaining').textContent = `${progress.remaining} ml`;
        document.getElementById('waterScore').textContent = `${progress.percentage}%`;
        
        const waterProgress = document.getElementById('waterProgress');
        waterProgress.style.width = `${Math.min(100, progress.percentage)}%`;
        
        // Change color based on progress
        if (progress.percentage >= 100) {
            waterProgress.style.background = 'linear-gradient(90deg, #27ae60, #2ecc71)';
        } else if (progress.percentage >= 75) {
            waterProgress.style.background = 'linear-gradient(90deg, #3498db, #2ecc71)';
        } else if (progress.percentage >= 50) {
            waterProgress.style.background = 'linear-gradient(90deg, #3498db, #5dade2)';
        } else {
            waterProgress.style.background = 'linear-gradient(90deg, #e74c3c, #ec7063)';
        }
    }
    
    updateCaloriesSummary() {
        const mealCalories = this.getMealCalories();
        const totalCalories = this.getTotalCalories();
        
        document.getElementById('breakfastCalories').textContent = `${mealCalories.breakfast} cal`;
        document.getElementById('lunchCalories').textContent = `${mealCalories.lunch} cal`;
        document.getElementById('dinnerCalories').textContent = `${mealCalories.dinner} cal`;
        document.getElementById('snacksCalories').textContent = `${mealCalories.snacks} cal`;
        document.getElementById('totalCalories').textContent = `${totalCalories} cal`;
        
        const caloriesScore = this.calculateNutritionScore();
        const scoreElement = document.getElementById('caloriesScore');
        
        if (caloriesScore >= 80) {
            scoreElement.textContent = 'Excellent';
            scoreElement.style.background = '#27ae60';
        } else if (caloriesScore >= 60) {
            scoreElement.textContent = 'Good';
            scoreElement.style.background = '#f39c12';
        } else {
            scoreElement.textContent = 'Needs Attention';
            scoreElement.style.background = '#e74c3c';
        }
    }
    
    getMealCalories() {
        const dayData = this.plannerData[this.currentDate];
        const mealCalories = {
            breakfast: 0,
            lunch: 0,
            dinner: 0,
            snacks: 0
        };
        
        if (!dayData) return mealCalories;
        
        Object.keys(dayData).forEach(meal => {
            const selectedFoods = dayData[meal];
            let total = 0;
            
            selectedFoods.forEach(foodId => {
                const food = this.foodManager.getFood(foodId);
                if (food) {
                    total += food.calculateCalories();
                }
            });
            
            const mealKey = meal.toLowerCase();
            if (mealCalories.hasOwnProperty(mealKey)) {
                mealCalories[mealKey] = total;
            }
        });
        
        return mealCalories;
    }
    
    getTotalCalories() {
        const mealCalories = this.getMealCalories();
        return Object.values(mealCalories).reduce((sum, calories) => sum + calories, 0);
    }
    
    generateHealthMessage() {
        const waterScore = this.calculateWaterScore();
        const nutritionScore = this.calculateNutritionScore();
        const activitiesScore = this.calculateActivitiesScore();
        const totalCalories = this.getTotalCalories();
        
        // Calculate overall score for better categorization
        const overallScore = Math.round((activitiesScore + waterScore + nutritionScore) / 3);
        
        let message = '';
        
        if (overallScore >= 90) {
            message = `🌟 Excellent! Outstanding performance across all areas! You've maintained excellent hydration (${waterScore}%), nutrition (${nutritionScore}%), and activity completion (${activitiesScore}%). With ${totalCalories} calories consumed, you're at peak performance. Keep up this amazing momentum!`;
        } else if (overallScore >= 75) {
            message = `👏 Good job! You're performing well with ${waterScore}% water intake, ${nutritionScore}% nutrition score, and ${activitiesScore}% activity completion. Your ${totalCalories} calories show balanced eating. You're building healthy habits successfully!`;
        } else if (overallScore >= 60) {
            message = `📈 Improve! You're making progress but there's room to grow. Your water intake is ${waterScore}%, nutrition score is ${nutritionScore}%, and activities completed is ${activitiesScore}%. Focus on consistency - small adjustments will lead to significant improvements!`;
        } else {
            message = `🎯 Needs Attention! Today was challenging with ${waterScore}% water, ${nutritionScore}% nutrition, and ${activitiesScore}% activities. Don't get discouraged - every day is a fresh start. Focus on one area at a time to build momentum!`;
        }
        
        document.getElementById('healthMessage').textContent = message;
    }
    
    updateDetailedBreakdowns() {
        this.updateRoutineBreakdown();
        this.updateNutritionBreakdown();
        this.updateHydrationBreakdown();
    }
    
    updateRoutineBreakdown() {
        const routineBreakdown = document.getElementById('routineBreakdown');
        const dayData = this.plannerData[this.currentDate];
        
        if (!dayData) {
            routineBreakdown.innerHTML = '<p>No routine data available for this date.</p>';
            return;
        }
        
        let breakdownHTML = '<div class="routine-items">';
        
        Object.keys(dayData).forEach(meal => {
            const selectedFoods = dayData[meal];
            if (selectedFoods.length > 0) {
                breakdownHTML += `
                    <div class="routine-meal">
                        <h4>${meal}</h4>
                        <ul>
                `;
                
                selectedFoods.forEach(foodId => {
                    const food = this.foodManager.getFood(foodId);
                    if (food) {
                        breakdownHTML += `
                            <li>
                                ${food.name} - ${food.calculateCalories()} calories
                                <span class="category-tag">${food.category}</span>
                            </li>
                        `;
                    }
                });
                
                breakdownHTML += `
                        </ul>
                    </div>
                `;
            }
        });
        
        breakdownHTML += '</div>';
        routineBreakdown.innerHTML = breakdownHTML;
    }
    
    updateNutritionBreakdown() {
        const nutritionBreakdown = document.getElementById('nutritionBreakdown');
        const mealCalories = this.getMealCalories();
        const totalCalories = this.getTotalCalories();
        
        const nutritionHTML = `
            <div class="nutrition-overview">
                <h4>Caloric Distribution</h4>
                <div class="nutrition-chart">
                    ${Object.entries(mealCalories).map(([meal, calories]) => `
                        <div class="nutrition-bar">
                            <span class="bar-label">${meal.charAt(0).toUpperCase() + meal.slice(1)}</span>
                            <div class="bar-container">
                                <div class="bar-fill" style="width: ${(calories / totalCalories) * 100}%"></div>
                                <span class="bar-value">${calories} cal</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="nutrition-tips">
                    <p><strong>Total Calories:</strong> ${totalCalories}</p>
                    <p><strong>Daily Recommendation:</strong> 1800-2200 calories for most adults</p>
                    <p><strong>Balance:</strong> Aim for breakfast ~25%, lunch ~35%, dinner ~30%, snacks ~10%</p>
                </div>
            </div>
        `;
        
        nutritionBreakdown.innerHTML = nutritionHTML;
    }
    
    updateHydrationBreakdown() {
        const hydrationBreakdown = document.getElementById('hydrationBreakdown');
        const waterData = this.waterManager.waterData[this.currentDate];
        
        if (!waterData) {
            hydrationBreakdown.innerHTML = '<p>No hydration data available for this date.</p>';
            return;
        }
        
        const progress = this.waterManager.getWaterProgress(this.currentDate);
        
        let hydrationHTML = `
            <div class="hydration-overview">
                <h4>Water Intake Details</h4>
                <div class="hydration-stats">
                    <p><strong>Wake-up Time:</strong> ${waterData.wakeUpTime || 'Not set'}</p>
                    <p><strong>Daily Target:</strong> ${progress.target} ml</p>
                    <p><strong>Consumed:</strong> ${progress.consumed} ml</p>
                    <p><strong>Percentage:</strong> ${progress.percentage}%</p>
                </div>
                <h5>Time Slots:</h5>
                <div class="water-slots">
        `;
        
        if (waterData.slots) {
            waterData.slots.forEach((slot, index) => {
                const statusClass = slot.status;
                const percentage = slot.amount > 0 ? Math.round((slot.consumed / slot.amount) * 100) : 0;
                
                hydrationHTML += `
                    <div class="water-slot-item ${statusClass}">
                        <span class="slot-time">${slot.time}</span>
                        <span class="slot-progress">${slot.consumed}/${slot.amount} ml</span>
                        <div class="slot-bar">
                            <div class="slot-fill" style="width: ${percentage}%"></div>
                        </div>
                    </div>
                `;
            });
        }
        
        hydrationHTML += `
                </div>
            </div>
        `;
        
        hydrationBreakdown.innerHTML = hydrationHTML;
    }
    
    generateRecommendations() {
        const recommendations = [];
        const waterScore = this.calculateWaterScore();
        const nutritionScore = this.calculateNutritionScore();
        const activitiesScore = this.calculateActivitiesScore();
        
        // Water recommendations
        if (waterScore < 80) {
            recommendations.push({
                type: 'tip',
                icon: '💧',
                text: 'Increase water intake by setting hourly reminders. Try keeping a water bottle visible at all times.'
            });
        }
        
        // Nutrition recommendations
        if (nutritionScore < 70) {
            recommendations.push({
                type: 'tip',
                icon: '🥗',
                text: 'Focus on balanced meals with protein, complex carbs, and healthy fats. Meal prep can help ensure better nutrition.'
            });
        }
        
        if (this.getTotalCalories() < 1500) {
            recommendations.push({
                type: 'warning',
                icon: '⚠️',
                text: 'Your calorie intake seems low. Consider adding nutrient-dense snacks to maintain energy levels.'
            });
        }
        
        // Activity recommendations
        if (activitiesScore < 60) {
            recommendations.push({
                type: 'tip',
                icon: '📋',
                text: 'Plan your meals in advance to ensure consistent nutrition throughout the day.'
            });
        }
        
        // General recommendations
        if (waterScore >= 80 && nutritionScore >= 80) {
            recommendations.push({
                type: 'success',
                icon: '🌟',
                text: 'Excellent job! Maintain this momentum by continuing to prioritize hydration and balanced nutrition.'
            });
        }
        
        recommendations.push({
            type: 'tip',
            icon: '😴',
            text: 'Remember that quality sleep complements your nutrition and hydration efforts for optimal health.'
        });
        
        const recommendationList = document.getElementById('recommendationList');
        
        if (recommendations.length === 0) {
            recommendationList.innerHTML = '<p>Keep up the great work! No specific recommendations for tomorrow.</p>';
            return;
        }
        
        const recommendationHTML = recommendations.map(rec => `
            <div class="recommendation-item ${rec.type}">
                <span class="recommendation-icon">${rec.icon}</span>
                <span class="recommendation-text">${rec.text}</span>
            </div>
        `).join('');
        
        recommendationList.innerHTML = recommendationHTML;
    }
    
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }
    
    shareSummary() {
        const text = `My daily summary for ${this.currentDate}:
        
🎯 Overall Score: ${document.getElementById('scoreNumber').textContent}
💧 Water: ${document.getElementById('waterScore').textContent}
🔥 Calories: ${this.getTotalCalories()} cal
📋 Activities: ${document.getElementById('activitiesScore').textContent}

Health Insight: ${document.getElementById('healthMessage').textContent.substring(0, 100)}...`;
        
        if (navigator.share) {
            navigator.share({
                title: 'Daily Health Summary',
                text: text
            }).catch(err => console.log('Error sharing:', err));
        } else {
            // Fallback: Copy to clipboard
            navigator.clipboard.writeText(text).then(() => {
                alert('Summary copied to clipboard!');
            }).catch(() => {
                alert('Unable to share summary');
            });
        }
    }
}

// Add enhanced styling for summary components
const chartStyles = document.createElement('style');
chartStyles.textContent = `
    .activity-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        margin-bottom: 8px;
        border-radius: 6px;
        font-size: 14px;
    }
    
    .activity-item.completed {
        background: #d4edda;
        border-left: 3px solid #28a745;
    }
    
    .activity-item.missed {
        background: #f8f9fa;
        border-left: 3px solid #6c757d;
    }
    
    .score-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        position: relative;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .score-circle:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .score-number {
        font-size: 2rem;
        font-weight: bold;
    }
    
    .score-label {
        font-weight: 600;
        font-size: 1.1rem;
        margin-top: 15px;
    }
    
    #healthMessage {
        font-size: 1.1rem;
        line-height: 1.6;
        padding: 15px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }
    
    .no-data {
        color: #6c757d;
        font-style: italic;
        text-align: center;
        padding: 20px;
    }
    
    .routine-meal {
        margin-bottom: 20px;
    }
    
    .routine-meal h4 {
        color: #2c3e50;
        margin-bottom: 10px;
        border-bottom: 2px solid #3498db;
        padding-bottom: 5px;
    }
    
    .routine-meal ul {
        list-style: none;
        padding-left: 0;
    }
    
    .routine-meal li {
        padding: 8px 12px;
        margin-bottom: 5px;
        background: #f8f9fa;
        border-radius: 5px;
        border-left: 3px solid #3498db;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .category-tag {
        background: #3498db;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
    }
    
    .nutrition-bar {
        margin-bottom: 15px;
    }
    
    .bar-label {
        font-weight: 600;
        color: #2c3e50;
        display: inline-block;
        width: 100px;
    }
    
    .bar-container {
        display: inline-block;
        width: 200px;
        height: 20px;
        background: #ecf0f1;
        border-radius: 10px;
        position: relative;
        vertical-align: middle;
    }
    
    .bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #3498db, #2ecc71);
        border-radius: 10px;
    }
    
    .bar-value {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 12px;
        font-weight: bold;
        color: #2c3e50;
    }
    
    .nutrition-tips {
        margin-top: 20px;
        padding: 15px;
        background: #e8f5e8;
        border-radius: 8px;
    }
    
    .hydration-stats {
        margin-bottom: 20px;
    }
    
    .hydration-stats p {
        margin-bottom: 8px;
    }
    
    .water-slots {
        display: grid;
        gap: 10px;
    }
    
    .water-slot-item {
        display: grid;
        grid-template-columns: 80px 1fr 100px;
        gap: 10px;
        align-items: center;
        padding: 10px;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    .slot-time {
        font-weight: 600;
        color: #2c3e50;
    }
    
    .slot-progress {
        font-size: 14px;
        color: #666;
    }
    
    .slot-bar {
        width: 100%;
        height: 8px;
        background: #ecf0f1;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .slot-fill {
        height: 100%;
        background: linear-gradient(90deg, #3498db, #2ecc71);
        border-radius: 4px;
    }
    
    .water-slot-item.completed .slot-fill {
        background: linear-gradient(90deg, #27ae60, #2ecc71);
    }
    
    .water-slot-item.partial .slot-fill {
        background: linear-gradient(90deg, #f39c12, #f1c40f);
    }
`;
document.head.appendChild(chartStyles);

// Initialize the summary page
let dailySummary;
document.addEventListener('DOMContentLoaded', () => {
    dailySummary = new DailySummary();
});