#!/usr/bin/env python3
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liferoutine360.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User

def test_dashboard():
    # Ensure admin user exists
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Created admin user")
    
    client = Client()
    
    # Get login page
    response = client.get('/accounts/login/')
    csrf_token = response.cookies.get('csrftoken')
    
    # Login
    login_data = {
        'username': 'admin',
        'password': 'admin123',
        'csrfmiddlewaretoken': csrf_token.value if csrf_token else ''
    }
    
    response = client.post('/accounts/login/', login_data, follow=True)
    print(f"Login status: {response.status_code}")
    
    # Access dashboard
    response = client.get('/', follow=True)
    print(f"Dashboard status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode()
        if 'dashboard' in content.lower():
            print("✅ Dashboard loaded successfully!")
        else:
            print("⚠️ Dashboard page loaded but may have issues")
            # Check for error messages
            if 'error' in content.lower() or 'exception' in content.lower():
                print("❌ Errors found in dashboard")
    else:
        print(f"❌ Dashboard access failed with status {response.status_code}")

if __name__ == '__main__':
    test_dashboard()