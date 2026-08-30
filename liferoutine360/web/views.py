from django.shortcuts import render


def meal_planner(request):
    """Main product page: daily meal planner."""
    return render(request, 'web/index.html')


def daily_summary(request):
    """Product page: end-of-day health summary."""
    return render(request, 'web/summary.html')


def water_tracker(request):
    """Product page: water intake tracker."""
    return render(request, 'web/water-tracker.html')


def food_admin(request):
    """Product page: food and ingredient catalogue admin."""
    return render(request, 'web/admin.html')