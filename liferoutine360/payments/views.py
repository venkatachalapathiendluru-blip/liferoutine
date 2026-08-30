from django.shortcuts import render

def payments_home(request):
    return render(request, 'payments/home.html')

def subscription_list(request):
    return render(request, 'payments/subscription_list.html')

def billing_view(request):
    return render(request, 'payments/billing.html')
