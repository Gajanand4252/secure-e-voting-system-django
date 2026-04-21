#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Digital_Voting.settings')
django.setup()

from voter.models import Voted

print("=" * 60)
print("CLEARING ALL VOTED RECORDS")
print("=" * 60)

voted_records = Voted.objects.all()
count = voted_records.count()

print(f"\nFound {count} Voted records")

if count > 0:
    confirmation = input(f"\nDelete all {count} Voted records? (type 'yes' to confirm): ").strip().lower()
    
    if confirmation == 'yes':
        voted_records.delete()
        print(f"\n✅ Deleted {count} Voted records")
    else:
        print("❌ Cancelled")
else:
    print("ℹ️  No Voted records to delete")

# Verify
remaining = Voted.objects.count()
print(f"\n📊 Remaining Voted records: {remaining}")
print("=" * 60)
