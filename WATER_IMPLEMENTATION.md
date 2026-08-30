# Water Intake Engine Implementation

## Overview
The water intake engine is a comprehensive system for tracking and scheduling daily water intake while avoiding meal times. It integrates with the existing LifeRoutine360 Django application.

## Key Features

### 1. Water Target Options
- **2.0 Liters**: Basic hydration for sedentary individuals
- **2.5 Liters**: Recommended for most adults with moderate activity  
- **3.0 Liters**: For active individuals, athletes, or hot climates

### 2. Smart Scheduling
- Splits daily water target into 8-10 optimal time slots
- Automatically avoids water intake:
  - **30 minutes before meals**
  - **30 minutes after meals**
- Maintains 16-hour hydration window from wake up time

### 3. Tracking Capabilities
- **Planned water**: Total scheduled water intake
- **Consumed water**: Actual water intake tracked
- **Remaining water**: Difference between planned and consumed
- **Completion percentage**: Progress tracking

## Implementation Details

### Models (`water/models.py`)

#### WaterGoal
- Stores user's daily water intake goals
- Supports 2.0L, 2.5L, and 3.0L targets
- Tracks active periods and history

#### WaterSchedule  
- Daily water intake schedule for each user
- Links to water goals and wake up times
- Contains multiple time slots

#### WaterTimeSlot
- Individual water intake time slots
- Tracks scheduled time, amount, and consumption status
- Marks meal-restricted slots

### Engine (`water/engine.py`)

#### WaterIntakeEngine Class
- `generate_schedule()`: Creates optimal water schedules
- `_generate_time_slots()`: Core scheduling algorithm
- `get_or_create_schedule()`: Retrieves or creates schedules
- `get_water_summary()`: Provides comprehensive tracking data
- `mark_water_consumed()`: Updates consumption status
- `update_water_goal()`: Modifies user goals

#### Scheduling Algorithm
1. **Input Parameters**:
   - Water target (2.0/2.5/3.0 liters)
   - Wake up time
   - Meal times (breakfast, lunch, dinner)

2. **Restricted Periods**:
   - 30 minutes before each meal
   - 30 minutes after each meal

3. **Slot Generation**:
   - Creates 30-minute intervals from wake up time
   - Filters out restricted periods
   - Selects 8-10 optimal slots
   - Distributes water evenly across slots

### Views (`water/views.py`)

#### Web Interface
- `water_home()`: Dashboard with progress overview
- `water_track()`: Detailed tracking interface
- `water_history()`: 30-day history view
- `water_settings()`: Goal configuration

#### API Endpoints
- `api_water_summary()`: Get daily summary data
- `api_mark_consumed()`: Mark slots as consumed
- `api_generate_schedule()`: Create new schedules

### Templates (`templates/water/`)

#### Frontend Interface
- **home.html**: Dashboard with quick stats and features
- **track.html**: Interactive tracking with time slots
- **history.html**: Historical progress analysis
- **settings.html**: Goal configuration interface

## Database Schema

### Tables Created
1. `water_watergoal` - User water intake goals
2. `water_waterschedule` - Daily schedules
3. `water_watertimeslot` - Individual time slots

### Relationships
- User → WaterGoal (1:many)
- User → WaterSchedule (1:many) 
- WaterGoal → WaterSchedule (1:many)
- WaterSchedule → WaterTimeSlot (1:many)

## Integration Points

### With Planning Module
- Uses Timeline model for wake up and meal times
- Integrates with existing daily routine structure

### With User System
- Links to Django User model
- Supports authentication and authorization

### With Core Features
- Follows existing patterns and conventions
- Uses shared templates and styling

## Example Usage

### Creating a Schedule
```python
from liferoutine360.water.engine import WaterIntakeEngine

# Generate schedule for user
schedule = WaterIntakeEngine.generate_schedule(
    user=request.user,
    date=today,
    water_goal_liters=2.5,
    wake_up_time=time(6, 0),
    meal_times={
        'breakfast': time(9, 0),
        'lunch': time(13, 0), 
        'dinner': time(18, 0)
    }
)
```

### Tracking Consumption
```python
# Mark water as consumed
success = WaterIntakeEngine.mark_water_consumed(
    user=request.user,
    date=today,
    slot_time=time(8, 0),
    amount_ml=250
)
```

### Getting Summary
```python
# Get daily water summary
summary = WaterIntakeEngine.get_water_summary(request.user, today)
print(f"Consumed: {summary['consumed_ml']}ml")
print(f"Remaining: {summary['remaining_ml']}ml")
print(f"Completion: {summary['completion_percentage']}%")
```

## URL Structure

```
/water/                    # Water dashboard
/water/track/             # Tracking interface
/water/history/           # History view
/water/settings/          # Settings page

/water/api/summary/       # Get summary data
/water/api/mark-consumed/ # Mark as consumed
/water/api/generate-schedule/ # Create schedule
```

## Benefits

1. **Health Optimization**: Proper hydration timing improves digestion and nutrient absorption
2. **Habit Formation**: Structured schedule helps build consistent hydration habits
3. **Progress Tracking**: Comprehensive monitoring of daily and long-term progress
4. **Personalization**: Adapts to individual schedules and preferences
5. **Integration**: Seamlessly works with existing meal planning and routine features

## Future Enhancements

1. **Smart Reminders**: Push notifications for scheduled water intake
2. **Weather Integration**: Adjust targets based on temperature and humidity
3. **Activity Tracking**: Modify goals based on exercise and activity levels
4. **Analytics Dashboard**: Advanced insights and pattern recognition
5. **Mobile App**: Native mobile application for on-the-go tracking

This implementation provides a robust, scalable foundation for water intake tracking that enhances the overall LifeRoutine360 health management platform.