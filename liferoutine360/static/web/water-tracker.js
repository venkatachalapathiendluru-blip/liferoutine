class WaterTracker {
    constructor() {
        this.waterManager = new WaterIntakeManager();
        this.currentDate = new Date().toISOString().split('T')[0];
        this.currentSlotIndex = null;
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setDefaultValues();
        this.loadTodayData();
    }
    
    setupEventListeners() {
        // Control buttons
        document.getElementById('generateScheduleBtn').addEventListener('click', () => this.generateSchedule());
        
        // Date change
        document.getElementById('selectedDate').addEventListener('change', (e) => {
            this.currentDate = e.target.value;
            this.loadTodayData();
        });
        
        // Quick add buttons
        document.querySelectorAll('.water-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleQuickAdd(e.target));
        });
        
        // Custom amount
        document.getElementById('addCustomAmount').addEventListener('click', () => this.addCustomAmount());
        
        // Modal
        document.getElementById('consumeWaterBtn').addEventListener('click', () => this.consumeFromModal());
        document.querySelectorAll('.close, .cancel-btn').forEach(btn => {
            btn.addEventListener('click', () => this.closeModal());
        });
        
        // Click outside modal
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal();
            }
        });
    }
    
    setDefaultValues() {
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('selectedDate').value = today;
    }
    
    generateSchedule() {
        const wakeUpTime = document.getElementById('wakeUpTime').value;
        const dailyTarget = document.getElementById('dailyTarget').value;
        
        if (!wakeUpTime) {
            alert('Please select wake up time');
            return;
        }
        
        // Get or create water schedule
        const schedule = this.waterManager.getWaterSchedule(this.currentDate, wakeUpTime, dailyTarget);
        
        // Update UI
        this.renderSchedule(schedule);
        this.updateProgress();
        this.updateRecommendations();
    }
    
    renderSchedule(dayData) {
        const scheduleGrid = document.getElementById('scheduleGrid');
        
        if (!dayData || !dayData.slots || dayData.slots.length === 0) {
            scheduleGrid.innerHTML = `
                <div class="no-schedule">
                    <p>Generate a schedule to see your water intake plan</p>
                </div>
            `;
            return;
        }
        
        scheduleGrid.innerHTML = dayData.slots.map((slot, index) => `
            <div class="water-slot ${slot.status}" onclick="waterTracker.openSlotModal(${index})">
                <div class="water-slot-time">${slot.time}</div>
                <div class="water-slot-amount">${slot.amount} ml</div>
                <div class="water-slot-progress">${slot.consumed} / ${slot.amount} ml</div>
                <div class="water-slot-status ${slot.status}">${slot.status}</div>
            </div>
        `).join('');
    }
    
    updateProgress() {
        const progress = this.waterManager.getWaterProgress(this.currentDate);
        
        document.getElementById('targetAmount').textContent = `${progress.target} ml`;
        document.getElementById('consumedAmount').textContent = `${progress.consumed} ml`;
        document.getElementById('remainingAmount').textContent = `${progress.remaining} ml`;
        document.getElementById('progressPercentage').textContent = `${progress.percentage}%`;
        
        const progressBar = document.getElementById('progressBar');
        progressBar.style.width = `${Math.min(100, progress.percentage)}%`;
        
        // Change color based on progress
        if (progress.percentage >= 100) {
            progressBar.style.background = 'linear-gradient(90deg, #27ae60, #2ecc71)';
        } else if (progress.percentage >= 75) {
            progressBar.style.background = 'linear-gradient(90deg, #3498db, #2ecc71)';
        } else if (progress.percentage >= 50) {
            progressBar.style.background = 'linear-gradient(90deg, #3498db, #5dade2)';
        } else {
            progressBar.style.background = 'linear-gradient(90deg, #e74c3c, #ec7063)';
        }
    }
    
    updateRecommendations() {
        const recommendations = this.waterManager.getWaterRecommendations(this.currentDate);
        const recommendationsList = document.getElementById('recommendationsList');
        
        if (recommendations.length === 0) {
            recommendationsList.innerHTML = '<p class="no-recommendations">No current recommendations</p>';
            return;
        }
        
        recommendationsList.innerHTML = recommendations.map(rec => `
            <div class="recommendation-item ${rec.priority >= 8 ? 'urgent' : ''}">
                <span class="recommendation-time">${rec.time}</span>
                <span class="recommendation-amount">${rec.amount} ml</span>
            </div>
        `).join('');
    }
    
    openSlotModal(slotIndex) {
        const dayData = this.waterManager.waterData[this.currentDate];
        if (!dayData || !dayData.slots[slotIndex]) {
            return;
        }
        
        this.currentSlotIndex = slotIndex;
        const slot = dayData.slots[slotIndex];
        
        document.getElementById('modalTime').textContent = slot.time;
        document.getElementById('modalPlanned').textContent = `${slot.amount} ml`;
        document.getElementById('modalConsumed').textContent = `${slot.consumed} ml`;
        
        // Set max amount for input
        const remaining = slot.amount - slot.consumed;
        const modalAmount = document.getElementById('modalAmount');
        modalAmount.max = remaining;
        modalAmount.value = Math.min(250, remaining);
        
        document.getElementById('waterSlotModal').style.display = 'block';
    }
    
    consumeFromModal() {
        if (this.currentSlotIndex === null) {
            return;
        }
        
        const amount = parseInt(document.getElementById('modalAmount').value);
        if (!amount || amount <= 0) {
            alert('Please enter a valid amount');
            return;
        }
        
        const consumed = this.waterManager.consumeWater(this.currentDate, this.currentSlotIndex, amount);
        
        if (consumed > 0) {
            this.closeModal();
            this.refreshUI();
            
            // Show success feedback
            this.showSuccessFeedback(`Consumed ${consumed} ml of water!`);
        } else {
            alert('Unable to consume water. Please check the amount.');
        }
    }
    
    handleQuickAdd(button) {
        const amount = button.dataset.amount;
        
        if (amount === 'custom') {
            document.getElementById('customAmount').style.display = 'flex';
            return;
        }
        
        this.addWaterAmount(parseInt(amount));
    }
    
    addCustomAmount() {
        const input = document.getElementById('customAmountInput');
        const amount = parseInt(input.value);
        
        if (!amount || amount <= 0 || amount > 1000) {
            alert('Please enter a valid amount between 1 and 1000 ml');
            return;
        }
        
        this.addWaterAmount(amount);
        input.value = '';
        document.getElementById('customAmount').style.display = 'none';
    }
    
    addWaterAmount(amount) {
        // Find the best slot to add this water
        const dayData = this.waterManager.waterData[this.currentDate];
        if (!dayData) {
            alert('Please generate a schedule first');
            return;
        }
        
        const now = new Date();
        const currentTimeStr = now.toTimeString().slice(0, 5);
        
        // Find current or next available slot
        let bestSlotIndex = -1;
        let bestSlot = null;
        
        for (let i = 0; i < dayData.slots.length; i++) {
            const slot = dayData.slots[i];
            const remaining = slot.amount - slot.consumed;
            
            if (remaining >= amount) {
                if (slot.time <= currentTimeStr) {
                    // Current or past slot with remaining capacity
                    bestSlotIndex = i;
                    bestSlot = slot;
                    break;
                } else if (!bestSlot && slot.status === 'pending') {
                    // Next pending slot
                    bestSlotIndex = i;
                    bestSlot = slot;
                }
            }
        }
        
        if (bestSlotIndex === -1) {
            alert('No suitable slot found for this amount. Please use the schedule to add water.');
            return;
        }
        
        const consumed = this.waterManager.consumeWater(this.currentDate, bestSlotIndex, amount);
        
        if (consumed > 0) {
            this.refreshUI();
            this.showSuccessFeedback(`Added ${consumed} ml to ${bestSlot.time} slot!`);
        }
    }
    
    refreshUI() {
        const dayData = this.waterManager.waterData[this.currentDate];
        if (dayData) {
            this.renderSchedule(dayData);
            this.updateProgress();
            this.updateRecommendations();
        }
    }
    
    loadTodayData() {
        const dayData = this.waterManager.waterData[this.currentDate];
        
        if (dayData) {
            // Load existing settings
            document.getElementById('wakeUpTime').value = dayData.wakeUpTime || '06:00';
            
            // Find target from amount
            const target = dayData.target;
            let targetKey = '2.5L';
            if (target === 2000) targetKey = '2L';
            else if (target === 3000) targetKey = '3L';
            
            document.getElementById('dailyTarget').value = targetKey;
            
            this.renderSchedule(dayData);
            this.updateProgress();
            this.updateRecommendations();
        } else {
            // Clear UI if no data
            document.getElementById('scheduleGrid').innerHTML = `
                <div class="no-schedule">
                    <p>Generate a schedule to see your water intake plan</p>
                </div>
            `;
            this.updateProgress();
            this.updateRecommendations();
        }
    }
    
    closeModal() {
        document.getElementById('waterSlotModal').style.display = 'none';
        this.currentSlotIndex = null;
    }
    
    showSuccessFeedback(message) {
        // Create a temporary success message
        const feedback = document.createElement('div');
        feedback.className = 'success-feedback';
        feedback.textContent = message;
        feedback.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #27ae60;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 5px 20px rgba(39, 174, 96, 0.4);
            z-index: 2000;
            font-weight: 600;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(feedback);
        
        setTimeout(() => {
            feedback.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(feedback);
            }, 300);
        }, 3000);
    }
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize the water tracker
let waterTracker;
document.addEventListener('DOMContentLoaded', () => {
    waterTracker = new WaterTracker();
});