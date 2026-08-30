from django.contrib import admin
from .models import Module

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        """Only admins can add modules"""
        return request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN'
    
    def has_change_permission(self, request, obj=None):
        """Only admins can change modules"""
        return request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN'
    
    def has_delete_permission(self, request, obj=None):
        """Only admins can delete modules"""
        return request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN'
    
    def has_view_permission(self, request, obj=None):
        """Admins can view all, users can only view active modules"""
        if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'ADMIN':
            return True
        return request.user.is_authenticated
