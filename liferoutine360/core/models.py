from django.db import models

class Module(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'
        ordering = ['name']
    
    def __str__(self):
        return self.name