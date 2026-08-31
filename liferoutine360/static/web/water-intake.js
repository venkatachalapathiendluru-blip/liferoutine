class WaterIntakeManager {
    constructor() {
        this.dailyTargets = {
            '2L': 2000,
            '2.5L': 2500,
            '3L': 3000
        };
        
        this.mealTimes = {
            'Breakfast': { start: '07:00', end: '08:30', avoidAfter: 30 },
            'Lunch': { start: '12:00', end: '13:30', avoidAfter: 30 },
            'Dinner': { start: '18:00', end: '19:30', avoidAfter: 30 },
            'Snacks': { start: '10:00', end: '11:00', avoidAfter: 15 }
        };
        
        this.waterData = {};
        this.loadData();
    }
    
    generateWaterSlots(wakeUpTime, dailyTarget) {
        const targetML = this.dailyTargets[dailyTarget] || 2000;
        const slots = [];
        
        // Calculate optimal number of slots (8-12 slots per day)
        const slotCount = Math.max(8, Math.min(12, Math.ceil(targetML / 250)));
        const slotSize = Math.round(targetML / slotCount);
        
        // Generate time slots avoiding meal times
        const wakeUp = this.parseTime(wakeUpTime);
        const bedTime = new Date(wakeUp);
        bedTime.setHours(bedTime.getHours() + 16); // Assume 16 hours awake
        
        let currentTime = new Date(wakeUp);
        let slotIndex = 0;
        
        while (currentTime < bedTime && slotIndex < slotCount) {
            const timeStr = this.formatTime(currentTime);
            
            // Check if this time conflicts with meal avoidance
            if (!this.shouldAvoidWater(currentTime)) {
                slots.push({
                    time: timeStr,
                    amount: slotSize,
                    consumed: 0,
                    status: 'pending'
                });
                slotIndex++;
            }
            
            // Move to next slot (every 1-2 hours)
            currentTime = new Date(currentTime.getTime() + (90 * 60 * 1000)); // 90 minutes
        }
        
        // Adjust last few slots to meet exact target
        const totalPlanned = slots.reduce((sum, slot) => sum + slot.amount, 0);
        if (totalPlanned !== targetML) {
            const diff = targetML - totalPlanned;
            if (slots.length > 0) {
                slots[slots.length - 1].amount += diff;
            }
        }
        
        return slots;
    }
    
    shouldAvoidWater(currentTime) {
        const timeStr = this.formatTime(currentTime);
        
        for (const [meal, config] of Object.entries(this.mealTimes)) {
            const mealEnd = this.parseTime(config.end);
            const avoidUntil = new Date(mealEnd.getTime() + (config.avoidAfter * 60 * 1000));
            
            if (currentTime >= mealEnd && currentTime <= avoidUntil) {
                return true;
            }
        }
        
        return false;
    }
    
    getWaterSchedule(date, wakeUpTime, dailyTarget) {
        const dateKey = this.formatDateKey(date);
        
        if (!this.waterData[dateKey]) {
            this.waterData[dateKey] = {
                target: this.dailyTargets[dailyTarget] || 2000,
                wakeUpTime: wakeUpTime,
                slots: this.generateWaterSlots(wakeUpTime, dailyTarget),
                consumed: 0
            };
        }
        
        return this.waterData[dateKey];
    }
    
    consumeWater(date, slotIndex, amount) {
        const dateKey = this.formatDateKey(date);
        const dayData = this.waterData[dateKey];
        
        if (dayData && dayData.slots[slotIndex]) {
            const slot = dayData.slots[slotIndex];
            const actualAmount = Math.min(amount, slot.amount - slot.consumed);
            
            slot.consumed += actualAmount;
            dayData.consumed += actualAmount;
            
            // Update slot status
            if (slot.consumed >= slot.amount) {
                slot.status = 'completed';
            } else if (slot.consumed > 0) {
                slot.status = 'partial';
            }
            
            this.saveData();
            return actualAmount;
        }
        
        return 0;
    }
    
    getWaterProgress(date) {
        const dateKey = this.formatDateKey(date);
        const dayData = this.waterData[dateKey];
        
        if (!dayData) {
            return {
                target: 0,
                consumed: 0,
                percentage: 0,
                remaining: 0
            };
        }
        
        const percentage = dayData.target > 0 ? Math.round((dayData.consumed / dayData.target) * 100) : 0;
        
        return {
            target: dayData.target,
            consumed: dayData.consumed,
            percentage: percentage,
            remaining: Math.max(0, dayData.target - dayData.consumed)
        };
    }
    
    getWaterRecommendations(date) {
        const dateKey = this.formatDateKey(date);
        const dayData = this.waterData[dateKey];
        
        if (!dayData) {
            return [];
        }
        
        const now = new Date();
        const currentTimeStr = this.formatTime(now);
        
        return dayData.slots
            .filter(slot => slot.time <= currentTimeStr && slot.status === 'pending')
            .map(slot => ({
                time: slot.time,
                amount: slot.amount,
                priority: this.getSlotPriority(slot.time, currentTimeStr)
            }))
            .sort((a, b) => b.priority - a.priority);
    }
    
    getSlotPriority(slotTime, currentTime) {
        const slot = this.parseTime(slotTime);
        const current = this.parseTime(currentTime);
        const diffMinutes = (slot - current) / (1000 * 60);
        
        if (diffMinutes < 0) return 0; // Past slot
        if (diffMinutes <= 30) return 10; // Very urgent
        if (diffMinutes <= 60) return 8; // Urgent
        if (diffMinutes <= 120) return 5; // Normal
        return 3; // Low priority
    }
    
    // Utility methods
    parseTime(timeStr) {
        const [hours, minutes] = timeStr.split(':').map(Number);
        const date = new Date();
        date.setHours(hours, minutes, 0, 0);
        return date;
    }
    
    formatTime(date) {
        return date.toTimeString().slice(0, 5);
    }
    
    formatDateKey(date) {
        if (typeof date === 'string') {
            return date;
        }
        return date.toISOString().split('T')[0];
    }
    
    saveData() {
        localStorage.setItem('waterIntakeData', JSON.stringify(this.waterData));
    }
    
    loadData() {
        const savedData = localStorage.getItem('waterIntakeData');
        if (savedData) {
            try {
                this.waterData = JSON.parse(savedData);
            } catch (error) {
                console.error('Error loading water data:', error);
                this.waterData = {};
            }
        }
    }
    
    resetDay(date) {
        const dateKey = this.formatDateKey(date);
        delete this.waterData[dateKey];
        this.saveData();
    }
    
    getWeeklyStats(startDate, endDate) {
        const stats = [];
        const current = new Date(startDate);
        
        while (current <= endDate) {
            const dateKey = this.formatDateKey(current);
            const progress = this.getWaterProgress(dateKey);
            
            stats.push({
                date: dateKey,
                target: progress.target,
                consumed: progress.consumed,
                percentage: progress.percentage,
                achieved: progress.percentage >= 100
            });
            
            current.setDate(current.getDate() + 1);
        }
        
        return stats;
    }
}