from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Create a sample admin account for LifeRoutine 360'

    def handle(self, *args, **options):
        # Check if admin user already exists
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('Admin user already exists'))
            return

        # Create admin user
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@liferoutine360.com',
            password='Admin123!@#',
            first_name='Super',
            last_name='Admin',
            is_staff=True,
            is_superuser=True
        )

        # Create user profile
        profile = UserProfile.objects.create(
            user=admin_user,
            wake_up_time='06:00:00',
            sleep_time='22:00:00',
            plan='WEIGHT_LOSS',
            water_target_liters=3.0,
            food_preference='VEG',
            role='ADMIN'
        )

        self.stdout.write(self.style.SUCCESS(
            'Successfully created admin account:\n'
            'Username: admin\n'
            'Password: Admin123!@#\n'
            'Email: admin@liferoutine360.com'
        ))