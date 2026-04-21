"""
Script to delete registered voter details except admin users
and delete already voted voter records
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Digital_Voting.settings')
django.setup()

from django.contrib.auth.models import User
from EC_Admin.models import Voters
from voter.models import Voted

def cleanup_voters():
    """Delete registered voters (except admin/superuser) and voted records"""
    
    print("=" * 60)
    print("VOTER CLEANUP SCRIPT")
    print("=" * 60)
    
    # Get all non-superuser, non-staff users (registered voters)
    voter_users = User.objects.filter(is_superuser=False, is_staff=False)
    voter_count = voter_users.count()
    
    print(f"\nFound {voter_count} registered voter accounts (non-admin)")
    
    # Get corresponding Voters records
    voter_ids = [user.username for user in voter_users]
    voters_to_delete = Voters.objects.filter(voterid_no__in=voter_ids)
    voters_count = voters_to_delete.count()
    
    print(f"Found {voters_count} Voters records to delete")
    
    # Get voted records
    voted_records = Voted.objects.filter(voter_id__in=voter_ids, has_voted='yes')
    voted_count = voted_records.count()
    
    print(f"Found {voted_count} voting records (already voted)")
    
    # Ask for confirmation
    print("\n" + "=" * 60)
    print("SUMMARY OF DELETIONS:")
    print("=" * 60)
    print(f"Voter User Accounts: {voter_count}")
    print(f"Voter Details: {voters_count}")
    print(f"Voted Records: {voted_count}")
    print("=" * 60)
    
    confirmation = input("\nDo you want to proceed with deletion? (yes/no): ").strip().lower()
    
    if confirmation != 'yes':
        print("❌ Cleanup cancelled.")
        return
    
    # Delete voted records first
    if voted_count > 0:
        deleted_voted, _ = voted_records.delete()
        print(f"\n✅ Deleted {deleted_voted} voted records")
    
    # Delete Voters records
    if voters_count > 0:
        deleted_voters, _ = voters_to_delete.delete()
        print(f"✅ Deleted {deleted_voters} Voters details")
    
    # Delete User accounts
    if voter_count > 0:
        deleted_users, _ = voter_users.delete()
        print(f"✅ Deleted {deleted_users} User accounts")
    
    print("\n" + "=" * 60)
    print("✅ CLEANUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nRemaining data:")
    
    # Show remaining admin users
    admin_users = User.objects.filter(is_superuser=True)
    print(f"Admin accounts: {admin_users.count()}")
    for admin in admin_users:
        print(f"  - {admin.username}")
    
    # Show remaining voters
    remaining_voters = Voters.objects.all()
    print(f"\nRemaining Voters: {remaining_voters.count()}")
    
    # Show remaining voted records
    remaining_voted = Voted.objects.all()
    print(f"Remaining Voted records: {remaining_voted.count()}")

if __name__ == '__main__':
    cleanup_voters()
