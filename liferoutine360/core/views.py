from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Module
from .utils import user_has_admin_role
from planning.views import generate_timeline_for_user

@login_required
def module_list(request):
    """List all modules - admin sees all, users see only active ones"""
    if user_has_admin_role(request.user):
        modules = Module.objects.all()
    else:
        modules = Module.objects.filter(is_active=True)
    
    context = {
        'modules': modules,
        'is_admin': user_has_admin_role(request.user)
    }
    return render(request, 'core/module_list.html', context)

@login_required
def toggle_module(request, module_id):
    """Toggle module active status - admin only"""
    if not user_has_admin_role(request.user):
        messages.error(request, 'Admin access required')
        return redirect('module_list')
    
    module = get_object_or_404(Module, id=module_id)
    module.is_active = not module.is_active
    module.save()
    
    status = 'activated' if module.is_active else 'deactivated'
    messages.success(request, f'Module "{module.name}" {status} successfully')
    return redirect('module_list')

@login_required
def create_module(request):
    """Create new module - admin only"""
    if not user_has_admin_role(request.user):
        messages.error(request, 'Admin access required')
        return redirect('module_list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if Module.objects.filter(name=name).exists():
            messages.error(request, 'Module with this name already exists')
        else:
            Module.objects.create(name=name, description=description, is_active=True)
            messages.success(request, f'Module "{name}" created successfully')
            return redirect('module_list')
    
    return render(request, 'core/create_module.html')

def dashboard(request):
    """Generate today's timeline and display dashboard"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    # Generate today's timeline if it doesn't exist
    from datetime import date
    generate_timeline_for_user(request.user, date.today())
    
    return render(request, 'core/dashboard.html')

def home(request):
    return render(request, 'core/home.html')
