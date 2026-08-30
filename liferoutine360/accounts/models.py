from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    PLAN_CHOICES = [
        ('DIABETES', 'Diabetes'),
        ('WEIGHT_LOSS', 'Weight Loss'),
        ('WEIGHT_GAIN', 'Weight Gain'),
    ]
    
    FOOD_CHOICES = [
        ('VEG', 'Vegetarian'),
        ('NON_VEG', 'Non-Vegetarian'),
    ]
    
    ROLE_CHOICES = [
        ('USER', 'User'),
        ('ADMIN', 'Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    wake_up_time = models.TimeField(null=True, blank=True)
    sleep_time = models.TimeField(null=True, blank=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='WEIGHT_LOSS')
    water_target_liters = models.FloatField(default=2.5)
    food_preference = models.CharField(max_length=10, choices=FOOD_CHOICES, default='VEG')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
