from django.core.exceptions import ObjectDoesNotExist
from .models import Module

def is_module_active(module_name):
    """Check if a module is active"""
    try:
        module = Module.objects.get(name=module_name)
        return module.is_active
    except ObjectDoesNotExist:
        return False

def user_has_admin_role(user):
    """Check if user has admin role"""
    if not user.is_authenticated:
        return False
    return hasattr(user, 'profile') and user.profile.role == 'ADMIN'

def require_admin_role():
    """Decorator to require admin role"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not user_has_admin_role(request.user):
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("Admin access required")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_module_access(module_name):
    """Decorator to require module access"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not is_module_active(module_name):
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden(f"Module '{module_name}' is not active")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator