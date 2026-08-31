import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

from .forms import CustomUserCreationForm, UserProfileForm
from .models import UserProfile

UserModel = get_user_model()


def _google_configured():
    return bool(getattr(settings, 'GOOGLE_CLIENT_ID', ''))


@require_http_methods(['POST'])
@csrf_exempt
def google_auth(request):
    """Verify a Google Identity Services ID token and log the user in.

    This mirrors DevPrep's approach: the frontend "Continue with Google"
    button returns a credential (ID token), which we verify against Google.
    """
    if not _google_configured():
        return JsonResponse({'error': 'Google Sign-In is not configured.'}, status=503)

    try:
        data = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        data = {}
    credential = data.get('credential') or request.POST.get('credential')
    if not credential:
        return JsonResponse({'error': 'Missing Google credential.'}, status=400)

    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests

    try:
        profile = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError:
        return JsonResponse({'error': 'Invalid Google credential.'}, status=401)

    email = (profile.get('email') or '').lower()
    if not email or not profile.get('email_verified'):
        return JsonResponse({'error': 'Google account has no verified email.'}, status=401)

    # Find or create the user
    try:
        user = UserModel.objects.get(email=email)
    except UserModel.DoesNotExist:
        username = _make_unique_username(email.split('@')[0])
        first_name = profile.get('given_name', '') or ''
        last_name = profile.get('family_name', '') or ''
        user = UserModel.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        # UserProfile is auto-created via the post_save signal.

    login(request, user)
    data = {
        'name': user.first_name or user.username,
        'redirect': reverse('web:meal_planner'),
    }
    return JsonResponse(data)


def _make_unique_username(base):
    username = base
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f'{base}{counter}'
        counter += 1
    return username

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('web:meal_planner')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    # Add form-control class to form fields
    form.fields['username'].widget.attrs.update({'class': 'form-control'})
    form.fields['password'].widget.attrs.update({'class': 'form-control'})
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'google_configured': bool(_google_configured()),
        'GOOGLE_CLIENT_ID': settings.GOOGLE_CLIENT_ID,
    })

def logout_view(request):
    messages.success(request, 'You have been successfully logged out.')
    return redirect('accounts:login')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            first_name = form.cleaned_data.get('first_name')
            
            # Profile will be created automatically via signal
            messages.success(request, f'Account created successfully for {first_name}! Welcome to LifeRoutine 360.')
            login(request, user)
            return redirect('web:meal_planner')
        else:
            # Add form errors as messages
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field.replace("_", " ").title()}: {error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'google_configured': bool(_google_configured()),
        'GOOGLE_CLIENT_ID': settings.GOOGLE_CLIENT_ID,
    })

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    # Profile will be created automatically via signal
    try:
        profile = request.user.profile
    except:
        messages.error(request, 'Profile not found. Please contact support.')
        return redirect('web:meal_planner')
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile
    }
    return render(request, 'accounts/profile.html', context)
