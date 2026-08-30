from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from datetime import datetime, date, time, timedelta
import json

from .models import Timeline, TimelineSettings, MealDay, MealItem, Food, NutritionGoal
from .forms import MealItemForm, MealPlanForm
from .utils import get_date_range, auto_generate_meal_plan
from accounts.models import UserProfile
from routine_engine import generate_timeline_data, get_activity_descriptions_for_plan


def generate_timeline_for_user(user, target_date=None):
    """
    Generate and store timeline for a user for a specific date.
    
    Args:
        user: User object
        target_date: Date object (defaults to today)
        
    Returns:
        List of Timeline objects
    """
    
    if target_date is None:
        target_date = date.today()
    
    wake_up_time = time(6, 0)  # Default to 6:00 AM
    profile = None
    try:
        profile = user.profile
        if profile.wake_up_time:
            wake_up_time = profile.wake_up_time
    except UserProfile.DoesNotExist:
        pass
    
    # Generate timeline data
    timeline_data = generate_timeline_data(wake_up_time)
    
    # Get personalized descriptions
    if profile:
        try:
            descriptions = get_activity_descriptions_for_plan(profile.plan, profile.food_preference)
            
            # Update descriptions in timeline data
            for item in timeline_data:
                if item['activity_type'] in descriptions:
                    item['description'] = descriptions[item['activity_type']]
        except (UserProfile.DoesNotExist, AttributeError):
            pass
    
    # Get or create timeline settings
    settings, created = TimelineSettings.objects.get_or_create(user=user)
    
    # Create timeline entries
    timeline_objects = []
    
    # Delete existing timeline for this date
    Timeline.objects.filter(user=user, date=target_date).delete()
    
    for item in timeline_data:
        timeline = Timeline.objects.create(
            user=user,
            date=target_date,
            activity_type=item['activity_type'],
            activity_name=item['activity_name'],
            scheduled_time=item['scheduled_time'],
            offset_minutes=item['offset_minutes'],
            description=item['description']
        )
        timeline_objects.append(timeline)
    
    return timeline_objects


@login_required
def timeline_api(request):
    """
    API endpoint to get timeline data for the current user.
    """
    
    if request.method == 'GET':
        target_date_str = request.GET.get('date')
        if target_date_str:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        else:
            target_date = date.today()
        
        # Generate timeline if it doesn't exist
        existing_timeline = Timeline.objects.filter(user=request.user, date=target_date)
        
        if not existing_timeline.exists():
            generate_timeline_for_user(request.user, target_date)
            existing_timeline = Timeline.objects.filter(user=request.user, date=target_date)
        
        # Format data for JSON response
        timeline_data = []
        for item in existing_timeline.order_by('scheduled_time'):
            timeline_data.append({
                'id': item.id,
                'activity_type': item.activity_type,
                'activity_name': item.activity_name,
                'scheduled_time': item.scheduled_time.strftime('%H:%M'),
                'offset_minutes': item.offset_minutes,
                'description': item.description,
                'is_completed': item.is_completed,
                'completed_at': item.completed_at.isoformat() if item.completed_at else None
            })
        
        return JsonResponse({
            'status': 'success',
            'date': target_date_str if target_date_str else target_date.isoformat(),
            'timeline': timeline_data
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@login_required
@require_http_methods(['POST'])
def complete_activity(request, activity_id):
    """
    Mark an activity as completed.
    """
    
    try:
        timeline = Timeline.objects.get(id=activity_id, user=request.user)
        timeline.mark_completed()
        
        return JsonResponse({
            'status': 'success',
            'message': f'{timeline.activity_name} marked as completed'
        })
    except Timeline.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Activity not found'
        }, status=404)


@login_required
@require_http_methods(['POST'])
def uncomplete_activity(request, activity_id):
    """
    Mark an activity as not completed.
    """
    
    try:
        timeline = Timeline.objects.get(id=activity_id, user=request.user)
        timeline.is_completed = False
        timeline.completed_at = None
        timeline.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'{timeline.activity_name} marked as incomplete'
        })
    except Timeline.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Activity not found'
        }, status=404)


def planning_home(request):
    return render(request, 'planning/home.html')

def task_list(request):
    return render(request, 'planning/task_list.html')

def task_create(request):
    return render(request, 'planning/task_create.html')

def task_detail(request, pk):
    return render(request, 'planning/task_detail.html')


@login_required
def meal_planner_api(request):
    """
    API endpoint for meal planning operations
    """
    
    if request.method == 'GET':
        # Get meal plan for a specific date range
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        
        if not start_date_str:
            start_date = date.today()
        else:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        
        if not end_date_str:
            end_date = start_date
        else:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        meal_plans = []
        current_date = start_date
        
        while current_date <= end_date:
            meal_day, created = MealDay.objects.get_or_create(
                user=request.user,
                date=current_date
            )
            
            meal_items_data = []
            for meal_item in meal_day.get_meal_items():
                meal_items_data.append({
                    'id': meal_item.id,
                    'meal_type': meal_item.meal_type,
                    'meal_type_display': meal_item.get_meal_type_display(),
                    'food': meal_item.food_name or (meal_item.food.name if meal_item.food else 'Unknown'),
                    'quantity': str(meal_item.quantity),
                    'quantity_unit': meal_item.quantity_unit,
                    'quantity_unit_display': meal_item.get_quantity_unit_display(),
                    'calories': meal_item.get_calories(),
                    'notes': meal_item.notes
                })
            
            # Calculate calorie breakdown
            calories_breakdown = meal_day.get_calories_breakdown()
            goal_comparison = meal_day.compare_with_goal()
            
            meal_plans.append({
                'date': current_date.isoformat(),
                'meal_day_id': meal_day.id,
                'meal_items': meal_items_data,
                'calories_breakdown': calories_breakdown,
                'goal_comparison': goal_comparison
            })
            
            current_date += timedelta(days=1)
        
        return JsonResponse({
            'status': 'success',
            'meal_plans': meal_plans,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        })
    
    elif request.method == 'POST':
        # Add or update meal items
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            if 'date' not in data or 'meal_items' not in data:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Date and meal_items are required'
                }, status=400)
            
            target_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            
            # Get or create MealDay
            meal_day, created = MealDay.objects.get_or_create(
                user=request.user,
                date=target_date
            )
            
            # Clear existing meal items for this day
            MealItem.objects.filter(meal_day=meal_day).delete()
            
            # Create new meal items
            created_items = []
            for item_data in data['meal_items']:
                meal_item = MealItem.objects.create(
                    meal_day=meal_day,
                    meal_type=item_data['meal_type'],
                    food=item_data['food'],
                    quantity=item_data['quantity'],
                    quantity_unit=item_data.get('quantity_unit', 'serving'),
                    calories=item_data.get('calories'),
                    notes=item_data.get('notes', '')
                )
                created_items.append(meal_item.id)
            
            return JsonResponse({
                'status': 'success',
                'message': f'Meal plan for {target_date} saved successfully',
                'created_items': created_items
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    elif request.method == 'DELETE':
        # Delete meal plan for a specific date
        try:
            date_str = request.GET.get('date')
            if not date_str:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Date parameter is required'
                }, status=400)
            
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Delete meal day and all its items
            deleted_count = MealDay.objects.filter(
                user=request.user,
                date=target_date
            ).delete()[0]
            
            return JsonResponse({
                'status': 'success',
                'message': f'Meal plan for {target_date} deleted successfully',
                'deleted_count': deleted_count
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@login_required
def calorie_tracking_api(request):
    """
    API endpoint for calorie tracking and nutrition goals
    """
    
    if request.method == 'GET':
        # Get calorie data for a date range
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        
        if not start_date_str:
            start_date = date.today()
        else:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        
        if not end_date_str:
            end_date = start_date
        else:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        # Get nutrition goal
        try:
            nutrition_goal = NutritionGoal.objects.get(user=request.user, is_active=True)
            goal_data = {
                'id': nutrition_goal.id,
                'goal_type': nutrition_goal.goal_type,
                'goal_type_display': nutrition_goal.get_goal_type_display(),
                'daily_calorie_target': nutrition_goal.daily_calorie_target,
                'tolerance_calories': nutrition_goal.tolerance_calories,
                'start_date': nutrition_goal.start_date.isoformat(),
                'end_date': nutrition_goal.end_date.isoformat() if nutrition_goal.end_date else None,
                'notes': nutrition_goal.notes
            }
        except NutritionGoal.DoesNotExist:
            goal_data = None
        
        # Get calorie data for each day
        calorie_data = []
        current_date = start_date
        
        while current_date <= end_date:
            try:
                meal_day = MealDay.objects.get(user=request.user, date=current_date)
                calories_breakdown = meal_day.get_calories_breakdown()
                goal_comparison = meal_day.compare_with_goal()
            except MealDay.DoesNotExist:
                calories_breakdown = {
                    'breakfast': 0,
                    'lunch': 0,
                    'snacks': 0,
                    'dinner': 0,
                    'total': 0
                }
                goal_comparison = {
                    'actual': 0,
                    'target': goal_data['daily_calorie_target'] if goal_data else None,
                    'difference': None,
                    'percentage_diff': None,
                    'goal_type': goal_data['goal_type'] if goal_data else None,
                    'is_on_track': None
                }
            
            calorie_data.append({
                'date': current_date.isoformat(),
                'calories_breakdown': calories_breakdown,
                'goal_comparison': goal_comparison
            })
            
            current_date += timedelta(days=1)
        
        return JsonResponse({
            'status': 'success',
            'nutrition_goal': goal_data,
            'calorie_data': calorie_data,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        })
    
    elif request.method == 'POST':
        # Create or update nutrition goal
        try:
            data = json.loads(request.body)
            
            # Deactivate existing goals
            NutritionGoal.objects.filter(user=request.user, is_active=True).update(is_active=False)
            
            # Create new goal
            nutrition_goal = NutritionGoal.objects.create(
                user=request.user,
                goal_type=data['goal_type'],
                daily_calorie_target=data['daily_calorie_target'],
                tolerance_calories=data.get('tolerance_calories', 100),
                start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
                end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
                notes=data.get('notes', ''),
                is_active=True
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Nutrition goal created successfully',
                'goal_id': nutrition_goal.id
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@login_required
def meal_planner_home(request):
    """Main meal planning page"""
    form = MealPlanForm()
    return render(request, 'planning/meal_planner.html', {'form': form})


@login_required
def auto_generate_meal_plan_api(request):
    """
    Auto-generate meal plan for a date range
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            plan_type = data.get('plan_type', 'tomorrow')
            start_date_str = data.get('start_date')
            end_date_str = data.get('end_date')
            
            # Parse dates
            start_date = None
            end_date = None
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            # Get date range
            start_date, end_date = get_date_range(plan_type, start_date, end_date)
            
            # Get user's food preference
            try:
                profile = request.user.profile
                food_preference = profile.food_preference
            except UserProfile.DoesNotExist:
                food_preference = 'VEG'
            
            # Generate meal plans for each date
            generated_plans = []
            current_date = start_date
            
            while current_date <= end_date:
                created_items = auto_generate_meal_plan(
                    request.user, 
                    current_date, 
                    food_preference
                )
                generated_plans.append({
                    'date': current_date.isoformat(),
                    'items_created': len(created_items)
                })
                current_date += timedelta(days=1)
            
            return JsonResponse({
                'status': 'success',
                'message': f'Generated meal plans from {start_date} to {end_date}',
                'generated_plans': generated_plans
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
