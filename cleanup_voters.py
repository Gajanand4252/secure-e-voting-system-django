#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Digital_Voting.settings')
django.setup()

from django.contrib.auth.models import User
from EC_Admin.models import Voters
from voter.models import Voted

print("=" * 60)
print("VOTER CLEANUP - DELETE REGISTERED VOTERS & VOTING RECORDS")
print("=" * 60)

# Get all non-superuser, non-staff users (registered voters)
voter_users = User.objects.filter(is_superuser=False, is_staff=False)
voter_count = voter_users.count()
print(f"\nFound {voter_count} registered voter accounts (non-admin)")

# Get voter IDs
voter_ids = list(voter_users.values_list('username', flat=True))

# Get corresponding Voters records
voters_to_delete = Voters.objects.filter(voterid_no__in=voter_ids)
voters_count = voters_to_delete.count()
print(f"Found {voters_count} Voters records to delete")

# Get voted records
voted_records = Voted.objects.filter(voter_id__in=voter_ids, has_voted='yes')
voted_count = voted_records.count()
print(f"Found {voted_count} voting records (already voted)")

print("\n" + "=" * 60)
print("SUMMARY OF DELETIONS:")
print(f"  • Voter User Accounts: {voter_count}")
print(f"  • Voter Details: {voters_count}")
print(f"  • Voted Records: {voted_count}")
print("=" * 60)

# Ask for confirmation
confirmation = input("\n⚠️  Do you want to PERMANENTLY DELETE these records? (type 'yes' to confirm): ").strip().lower()

if confirmation != 'yes':
    print("❌ Cleanup cancelled.")
    sys.exit(0)

# Proceed with deletion
print("\n🔄 Processing deletion...")

if voted_count > 0:
    voted_records.delete()
    print(f"✅ Deleted {voted_count} voted records")

if voters_count > 0:
    voters_to_delete.delete()
    print(f"✅ Deleted {voters_count} Voters details")

if voter_count > 0:
    voter_users.delete()
    print(f"✅ Deleted {voter_count} User accounts")

print("\n" + "=" * 60)
print("✅ CLEANUP COMPLETED SUCCESSFULLY!")
print("=" * 60)

# Show remaining data
admin_users = User.objects.filter(is_superuser=True)
remaining_voters = Voters.objects.all()
remaining_voted = Voted.objects.all()

print(f"\n📊 REMAINING DATA:")
print(f"  • Admin accounts: {admin_users.count()}")
for admin in admin_users:
    print(f"    - {admin.username}")

print(f"  • Voters: {remaining_voters.count()}")
print(f"  • Voted records: {remaining_voted.count()}")
print("=" * 60)
