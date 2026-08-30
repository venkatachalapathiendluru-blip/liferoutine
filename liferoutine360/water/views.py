from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, date, time

from .models import WaterGoal, WaterSchedule, WaterTimeSlot
from .engine import WaterIntakeEngine


@login_required
def water_home(request):
    """Water intake dashboard"""
    today = date.today()
    
    # Get or create today's schedule
    schedule = WaterIntakeEngine.get_or_create_schedule(request.user, today)
    
    if schedule:
        summary = WaterIntakeEngine.get_water_summary(request.user, today)
        time_slots = schedule.get_time_slots()
    else:
        summary = None
        time_slots = []
    
    # Get user's water goals
    goals = WaterGoal.objects.filter(user=request.user).order_by('-created_at')
    current_goal = goals.filter(is_active=True).first()
    
    context = {
        'summary': summary,
        'time_slots': time_slots,
        'current_goal': current_goal,
        'goals': goals,
        'today': today
    }
    
    return render(request, 'water/home.html', context)


@login_required
def water_track(request):
    """Water tracking page"""
    today = date.today()
    
    # Get schedule for today
    try:
        schedule = WaterSchedule.objects.get(user=request.user, date=today)
        time_slots = schedule.get_time_slots()
        summary = WaterIntakeEngine.get_water_summary(request.user, today)
    except WaterSchedule.DoesNotExist:
        schedule = None
        time_slots = []
        summary = None
    
    context = {
        'schedule': schedule,
        'time_slots': time_slots,
        'summary': summary,
        'today': today
    }
    
    return render(request, 'water/track.html', context)


@login_required
def water_history(request):
    """Water intake history"""
    # Get last 30 days of schedules
    today = date.today()
    start_date = today - timezone.timedelta(days=30)
    
    schedules = WaterSchedule.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=today
    ).order_by('-date')
    
    # Prepare history data
    history_data = []
    for schedule in schedules:
        summary = WaterIntakeEngine.get_water_summary(request.user, schedule.date)
        history_data.append({
            'date': schedule.date,
            'target_liters': summary['target_liters'] if summary else 0,
            'consumed_ml': summary['consumed_ml'] if summary else 0,
            'completion_percentage': summary['completion_percentage'] if summary else 0,
            'time_slots_completed': len([s for s in schedule.time_slots.all() if s.is_consumed]),
            'total_time_slots': schedule.time_slots.count()
        })
    
    context = {
        'history_data': history_data,
        'start_date': start_date,
        'end_date': today
    }
    
    return render(request, 'water/history.html', context)


@login_required
def water_settings(request):
    """Water intake settings"""
    if request.method == 'POST':
        water_target = float(request.POST.get('water_target', 2.5))
        
        try:
            WaterIntakeEngine.update_water_goal(request.user, water_target)
            messages.success(request, f'Water goal updated to {water_target} liters per day')
            return redirect('water_home')
        except ValueError as e:
            messages.error(request, str(e))
    
    # Get current goal
    current_goal = WaterGoal.objects.filter(user=request.user, is_active=True).first()
    
    context = {
        'current_goal': current_goal
    }
    
    return render(request, 'water/settings.html', context)


# API Views
@login_required
def api_water_summary(request, target_date=None):
    """API endpoint to get water summary for a date"""
    if target_date:
        try:
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        except ValueError:
            target_date = date.today()
    else:
        target_date = date.today()
    
    summary = WaterIntakeEngine.get_water_summary(request.user, target_date)
    
    if summary:
        return JsonResponse({
            'success': True,
            'data': summary
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'No water schedule found for this date'
        })


@login_required
def api_mark_consumed(request):
    """API endpoint to mark water as consumed"""
    if request.method == 'POST':
        slot_time_str = request.POST.get('slot_time')
        target_date_str = request.POST.get('date')
        amount_ml = request.POST.get('amount_ml')
        
        if not slot_time_str or not target_date_str:
            return JsonResponse({
                'success': False,
                'message': 'Missing required parameters'
            })
        
        try:
            # Parse time and date
            slot_time = datetime.strptime(slot_time_str, '%H:%M').time()
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            
            # Convert amount to int if provided
            if amount_ml:
                amount_ml = int(amount_ml)
            else:
                amount_ml = None
            
            # Mark as consumed
            success = WaterIntakeEngine.mark_water_consumed(
                request.user, target_date, slot_time, amount_ml
            )
            
            if success:
                # Get updated summary
                summary = WaterIntakeEngine.get_water_summary(request.user, target_date)
                return JsonResponse({
                    'success': True,
                    'message': 'Water intake marked as consumed',
                    'data': summary
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Failed to mark water as consumed'
                })
                
        except (ValueError, TypeError) as e:
            return JsonResponse({
                'success': False,
                'message': f'Invalid data format: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Only POST method allowed'
    })


@login_required
def api_generate_schedule(request):
    """API endpoint to generate new water schedule"""
    if request.method == 'POST':
        target_date_str = request.POST.get('date')
        water_target = float(request.POST.get('water_target', 2.5))
        wake_up_time_str = request.POST.get('wake_up_time')
        
        if not target_date_str:
            return JsonResponse({
                'success': False,
                'message': 'Date is required'
            })
        
        try:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            
            if wake_up_time_str:
                wake_up_time = datetime.strptime(wake_up_time_str, '%H:%M').time()
            else:
                # Get from timeline or default
                from liferoutine360.planning.models import Timeline
                timeline = Timeline.objects.filter(
                    user=request.user,
                    date=target_date,
                    activity_type='wake_up'
                ).first()
                wake_up_time = timeline.scheduled_time if timeline else time(6, 0)
            
            # Get meal times
            meal_times = {}
            for meal_type in ['breakfast', 'lunch', 'dinner']:
                meal_timeline = Timeline.objects.filter(
                    user=request.user,
                    date=target_date,
                    activity_type=meal_type
                ).first()
                if meal_timeline:
                    meal_times[meal_type] = meal_timeline.scheduled_time
            
            # Generate schedule
            schedule = WaterIntakeEngine.generate_schedule(
                request.user, target_date, water_target, wake_up_time, meal_times
            )
            
            # Get summary
            summary = WaterIntakeEngine.get_water_summary(request.user, target_date)
            
            return JsonResponse({
                'success': True,
                'message': 'Water schedule generated successfully',
                'data': summary
            })
            
        except (ValueError, TypeError) as e:
            return JsonResponse({
                'success': False,
                'message': f'Invalid data format: {str(e)}'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Only POST method allowed'
    })
