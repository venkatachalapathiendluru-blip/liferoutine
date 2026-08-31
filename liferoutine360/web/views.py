from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def meal_planner(request):
    """Product page: daily meal planner."""
    return render(request, 'web/index.html')


@login_required
def daily_summary(request):
    """Product page: end-of-day health summary."""
    return render(request, 'web/summary.html')


@login_required
def water_tracker(request):
    """Product page: water intake tracker."""
    return render(request, 'web/water-tracker.html')


@login_required
def food_admin(request):
    """Product page: food and ingredient catalogue admin."""
    return render(request, 'web/admin.html')
