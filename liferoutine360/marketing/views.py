from django.shortcuts import render


def landing(request):
    """Public landing / marketing homepage."""
    return render(request, 'marketing/landing.html')


def features(request):
    """Public features overview page."""
    return render(request, 'marketing/features.html')


def pricing(request):
    """Public pricing page fed by plan definitions."""
    plans = [
        {
            'name': 'Free',
            'tagline': 'For getting started on your journey.',
            'price': '0',
            'billing': 'month',
            'featured': False,
            'features': [
                {'text': 'Daily meal planner', 'enabled': True},
                {'text': 'Water intake tracker', 'enabled': True},
                {'text': 'Food & calorie calculator', 'enabled': True},
                {'text': 'Daily health summary', 'enabled': True},
                {'text': 'Advanced analytics', 'enabled': False},
                {'text': 'Priority support', 'enabled': False},
            ],
        },
        {
            'name': 'Pro',
            'tagline': 'For those serious about their routine.',
            'price': '9',
            'billing': 'month',
            'featured': True,
            'features': [
                {'text': 'Everything in Free', 'enabled': True},
                {'text': 'Unlimited date-range planning', 'enabled': True},
                {'text': 'Advanced analytics & insights', 'enabled': True},
                {'text': 'Unlimited food database', 'enabled': True},
                {'text': 'Priority support', 'enabled': True},
            ],
        },
        {
            'name': 'Premium',
            'tagline': 'The complete wellness platform.',
            'price': '19',
            'billing': 'month',
            'featured': False,
            'features': [
                {'text': 'Everything in Pro', 'enabled': True},
                {'text': 'Personalized health coaching', 'enabled': True},
                {'text': 'Multi-profile management', 'enabled': True},
                {'text': 'Export & reporting tools', 'enabled': True},
                {'text': 'Dedicated support', 'enabled': True},
            ],
        },
    ]
    return render(request, 'marketing/pricing.html', {'plans': plans})


def about(request):
    """About us page."""
    return render(request, 'marketing/about.html')


def contact(request):
    """Contact page."""
    return render(request, 'marketing/contact.html')
