#!/usr/bin/env python
"""
Script to add EC Admin details to the database.
Run this after creating a superuser.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Digital_Voting.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from EC_Admin.models import EC_Admins
from django.contrib.auth.models import User
from datetime import date

def add_admin_details():
    """Add admin details from superuser to EC_Admins table"""
    try:
        # Get the superuser
        superuser = User.objects.filter(is_superuser=True).first()
        
        if not superuser:
            print("No superuser found. Please create a superuser first:")
            print("  python manage.py createsuperuser")
            return
        
        # Check if admin details already exist
        if EC_Admins.objects.filter(ecadmin_id=superuser.username).exists():
            print(f"Admin details for '{superuser.username}' already exist in EC_Admins table.")
            return
        
        # Create EC_Admin record
        admin = EC_Admins(
            ecadmin_id=superuser.username,
            firstname=superuser.first_name or superuser.username,
            lastname=superuser.last_name or "",
            middlename="",
            gender="M",
            dateofbirth=date(2000, 1, 1),  # Default date
            address="EC Admin",
            pincode="000000",
            mobile_no=1234567890,  # Default mobile
            email=superuser.email or "admin@election.com",
            ecadmin_image="ECAdminImage/default.jpg"  # Default image path
        )
        admin.save()
        print(f"✓ Successfully added EC Admin details for user: {superuser.username}")
        print(f"  - Email: {admin.email}")
        print(f"  - Mobile: {admin.mobile_no}")
        print("\nNote: Please update the admin profile with correct details:")
        print("  1. Log in to the admin panel")
        print("  2. Go to Admin Profile")
        print("  3. Update personal information and upload profile image")
        
    except Exception as e:
        print(f"✗ Error adding admin details: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    add_admin_details()
