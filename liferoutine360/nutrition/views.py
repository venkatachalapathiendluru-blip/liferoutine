from django.shortcuts import render

def nutrition_home(request):
    return render(request, 'nutrition/home.html')

def meal_list(request):
    return render(request, 'nutrition/meal_list.html')

def meal_create(request):
    return render(request, 'nutrition/meal_create.html')

def nutrition_track(request):
    return render(request, 'nutrition/track.html')
