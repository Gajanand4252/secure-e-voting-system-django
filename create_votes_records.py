#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Digital_Voting.settings')
django.setup()

from EC_Admin.models import Votes, Candidates, Election

print("=" * 60)
print("CREATE VOTES RECORDS FOR CANDIDATES")
print("=" * 60)

# Get all candidates
candidates = Candidates.objects.all()
print(f"\nFound {candidates.count()} candidates")

# Get all elections
elections = Election.objects.all()
print(f"Found {elections.count()} elections\n")

if not candidates.exists() or not elections.exists():
    print("❌ No candidates or elections found!")
    print("Please create candidates and elections first.")
    sys.exit(1)

# Create Votes records for each candidate-election combination
created_count = 0
for election in elections:
    for candidate in candidates:
        # Check if record already exists
        vote_record, created = Votes.objects.get_or_create(
            election_id=election.election_id,
            candidate_id=candidate.candidate_id,
            defaults={
                'candidate_name': candidate.name,
                'candidate_party': candidate.candidate_party,
                'state': candidate.state,
                'online_votes': 0,
                'evm_votes': 0,
                'total_votes': 0
            }
        )
        if created:
            created_count += 1
            print(f"✅ Created: {election.election_id} - {candidate.name}")
        else:
            print(f"ℹ️  Already exists: {election.election_id} - {candidate.name}")

print("\n" + "=" * 60)
print(f"✅ TOTAL RECORDS CREATED: {created_count}")
print("=" * 60)

# Show summary
all_votes = Votes.objects.count()
print(f"\nTotal Votes records in database: {all_votes}")
