#!/usr/bin/env python
"""
PostgreSQL Connection Verification Script
Run this to test if PostgreSQL is properly configured
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Digital_Voting.settings')
django.setup()

from django.db import connections
from django.db.utils import OperationalError, ProgrammingError
from django.core.management import call_command

print("=" * 70)
print("PostgreSQL Connection Verification Tool")
print("=" * 70)

# Test 1: Database Connection
print("\n[TEST 1] Testing Database Connection...")
try:
    conn = connections['default']
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    print("✅ PostgreSQL Connection Successful!")
    print(f"   Database: {conn.settings_dict['NAME']}")
    print(f"   User: {conn.settings_dict['USER']}")
    print(f"   Host: {conn.settings_dict['HOST']}:{conn.settings_dict['PORT']}")
    conn.close()
except OperationalError as e:
    print(f"❌ Connection Failed!")
    print(f"   Error: {e}")
    print("\n   SOLUTIONS:")
    print("   1. Ensure PostgreSQL service is running")
    print("   2. Check credentials in Digital_Voting/settings.py")
    print("   3. Verify database 'digital_voting' exists")
    print("   4. Verify user 'admin' exists with password 'admin123'")
    sys.exit(1)

# Test 2: Tables Exist
print("\n[TEST 2] Checking Database Tables...")
try:
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    if tables:
        print(f"✅ Found {len(tables)} tables in database")
        print(f"   Tables: {', '.join(sorted(tables)[:5])}...")
    else:
        print("⚠️  No tables found. Run migrations:")
        print("   python manage.py migrate")
    
    connection.close()
except Exception as e:
    print(f"❌ Error checking tables: {e}")

# Test 3: Models
print("\n[TEST 3] Checking Django Models...")
try:
    from EC_Admin.models import Voters, Candidates, Election, Votes, EC_Admins
    from voter.models import Voted, Complain, VoteOTP
    
    print("✅ All models imported successfully")
    print(f"   EC_Admin Models: Voters, Candidates, Election, Votes, EC_Admins")
    print(f"   Voter Models: Voted, Complain, VoteOTP")
    
    # Count records
    voters_count = Voters.objects.count()
    candidates_count = Candidates.objects.count()
    elections_count = Election.objects.count()
    
    print(f"\n   Database Contents:")
    print(f"   - Voters: {voters_count}")
    print(f"   - Candidates: {candidates_count}")
    print(f"   - Elections: {elections_count}")
    
except Exception as e:
    print(f"❌ Error importing models: {e}")

# Test 4: Migrations
print("\n[TEST 4] Checking Migrations...")
try:
    from django.core.management import call_command
    from io import StringIO
    
    out = StringIO()
    call_command('showmigrations', '--list', stdout=out)
    output = out.getvalue()
    
    if '[X]' in output:
        applied = output.count('[X]')
        print(f"✅ Migrations applied successfully")
        print(f"   Applied migrations: {applied}")
    else:
        print("⚠️  No migrations applied yet. Run:")
        print("   python manage.py migrate")
        
except Exception as e:
    print(f"❌ Error checking migrations: {e}")

# Test 5: User Accounts
print("\n[TEST 5] Checking User Accounts...")
try:
    from django.contrib.auth.models import User
    
    superusers = User.objects.filter(is_superuser=True)
    users = User.objects.all()
    
    print(f"✅ User accounts present")
    print(f"   Total users: {users.count()}")
    print(f"   Superusers: {superusers.count()}")
    
    if superusers.count() == 0:
        print("\n   ⚠️  No superuser found. Create one:")
        print("   python manage.py createsuperuser")
    
except Exception as e:
    print(f"❌ Error checking users: {e}")

print("\n" + "=" * 70)
print("Verification Complete!")
print("=" * 70)
print("\nNext Steps:")
print("1. If all tests passed, your system is ready to run")
print("2. Start development server: python manage.py runserver")
print("3. Access admin panel: http://localhost:8000/admin/")
print("4. Access voter portal: http://localhost:8000/")
print("=" * 70)
