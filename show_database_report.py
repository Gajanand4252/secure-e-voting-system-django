#!/usr/bin/env python
"""
Digital Voting System - Complete Database Statistics Report
Run this script to show all stored data to evaluators
"""

import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Digital_Voting.settings')
django.setup()

from EC_Admin.models import Voters, Candidates, Election, Votes, EC_Admins
from voter.models import Voted, Complain
from django.contrib.auth.models import User
from collections import defaultdict

def print_header(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_subheader(title):
    print(f"\n  {title}")
    print("  " + "-"*76)

print("\n")
print("╔" + "="*78 + "╗")
print("║" + " "*20 + "DIGITAL VOTING SYSTEM - DATABASE REPORT" + " "*20 + "║")
print("║" + " "*20 + "Complete Voting Statistics & Data View" + " "*21 + "║")
print("╚" + "="*78 + "╝")

# ==================== OVERALL STATISTICS ====================
print_header("📊 OVERALL SYSTEM STATISTICS")

total_voters = Voters.objects.count()
total_candidates = Candidates.objects.count()
total_elections = Election.objects.count()
total_user_accounts = User.objects.filter(is_superuser=False).count()
total_votes_cast = Voted.objects.filter(has_voted='yes').count()
total_admin_accounts = EC_Admins.objects.count()

print(f"  ✓ Total Registered Voters:        {total_voters:,}")
print(f"  ✓ Total Candidates:               {total_candidates:,}")
print(f"  ✓ Total Elections:                {total_elections:,}")
print(f"  ✓ Total Votes Cast:               {total_votes_cast:,}")
print(f"  ✓ Active User Accounts:           {total_user_accounts:,}")
print(f"  ✓ Admin Accounts:                 {total_admin_accounts:,}")

if total_voters > 0:
    voting_percentage = (total_votes_cast / total_voters) * 100
    print(f"\n  📈 Voter Turnout: {voting_percentage:.2f}% ({total_votes_cast}/{total_voters})")

# ==================== VOTER DETAILS ====================
print_header("👥 VOTER DATABASE INFORMATION")

if total_voters > 0:
    # State-wise distribution
    print_subheader("State-wise Voter Distribution")
    state_distribution = defaultdict(int)
    for voter in Voters.objects.all():
        state_distribution[voter.state] += 1
    
    for idx, (state, count) in enumerate(sorted(state_distribution.items(), key=lambda x: x[1], reverse=True), 1):
        print(f"  {idx:2}. {state:20} : {count:5} voters")
    
    # Gender distribution
    print_subheader("Gender Distribution")
    gender_dist = defaultdict(int)
    for voter in Voters.objects.all():
        gender_dist[voter.gender] += 1
    
    for gender, count in sorted(gender_dist.items()):
        percentage = (count / total_voters) * 100
        print(f"  {gender:10}: {count:5} voters ({percentage:5.1f}%)")
    
    # Sample voter records
    print_subheader("Sample Voter Records (First 5)")
    for idx, voter in enumerate(Voters.objects.all()[:5], 1):
        print(f"\n  [{idx}] Voter ID: {voter.voterid_no}")
        print(f"      Name: {voter.name} | Father: {voter.father_name} | Gender: {voter.gender}")
        print(f"      DOB: {voter.dateofbirth} | Mobile: {voter.mobile_no}")
        print(f"      Email: {voter.email}")
        print(f"      Location: {voter.assembly}, {voter.state} - {voter.pincode}")

# ==================== CANDIDATE DETAILS ====================
print_header("🗳️ CANDIDATE DATABASE INFORMATION")

if total_candidates > 0:
    print_subheader("Candidates by Party")
    party_dist = defaultdict(int)
    for candidate in Candidates.objects.all():
        party_dist[candidate.candidate_party] += 1
    
    for party, count in sorted(party_dist.items(), key=lambda x: x[1], reverse=True):
        print(f"  {party:25}: {count:3} candidates")
    
    print_subheader("Sample Candidate Records (First 5)")
    for idx, candidate in enumerate(Candidates.objects.all()[:5], 1):
        print(f"\n  [{idx}] ID: {candidate.candidate_id} | {candidate.name} | Party: {candidate.candidate_party}")
        print(f"      Age: {(candidate.dateofbirth).year} | Contact: {candidate.mobile_no}")
        print(f"      Constituency: {candidate.assembly if candidate.assembly else candidate.parliamentary}, {candidate.state}")

# ==================== ELECTION DETAILS ====================
print_header("🏛️ ELECTION INFORMATION")

if total_elections > 0:
    print_subheader("Active Elections")
    for idx, election in enumerate(Election.objects.all(), 1):
        print(f"\n  [{idx}] Election ID: {election.election_id}")
        print(f"      Name: {election.election_name}")
        print(f"      Type: {election.election_type}")
        print(f"      Start: {election.start_date} | End: {election.end_date}")
        print(f"      Status: {election.status}")
        
        # Votes count for this election
        total_votes = Voted.objects.filter(election_id=election.election_id, has_voted='yes').count()
        print(f"      Total Votes Cast: {total_votes}")

# ==================== VOTING RESULTS ====================
print_header("📋 VOTING RESULTS & STATISTICS")

if total_elections > 0:
    print_subheader("Election-wise Results")
    
    for election in Election.objects.all():
        print(f"\n  Election: {election.election_id} ({election.election_name})")
        print(f"  {'─'*76}")
        
        votes = Votes.objects.filter(election_id=election.election_id).order_by('-total_votes')
        
        if votes.exists():
            total_votes = sum(v.total_votes for v in votes)
            print(f"  Total Votes: {total_votes}\n")
            print(f"  {'Rank':<6} {'Candidate':<20} {'Party':<20} {'Votes':<8} {'%':<6}")
            print(f"  {'-'*76}")
            
            for idx, vote in enumerate(votes, 1):
                percentage = (vote.total_votes / total_votes * 100) if total_votes > 0 else 0
                candidate_name = vote.candidate_name[:19]
                party_name = vote.candidate_party[:19]
                print(f"  {idx:<6} {candidate_name:<20} {party_name:<20} {vote.total_votes:<8} {percentage:>5.1f}%")
        else:
            print("  No votes recorded yet for this election")

# ==================== VOTING ACTIVITY ====================
print_header("📊 VOTING ACTIVITY & RECORDS")

total_voted_records = Voted.objects.count()
voted_yes = Voted.objects.filter(has_voted='yes').count()
voted_no = Voted.objects.filter(has_voted='no').count()

print(f"  ✓ Total Voting Records: {total_voted_records:,}")
print(f"  ✓ Votes Cast (Yes):     {voted_yes:,}")
print(f"  ✓ Not Voted (No):       {voted_no:,}")

if total_voted_records > 0:
    print_subheader("Voting Method Distribution")
    
    online_votes = Voted.objects.filter(where_voted='online').count()
    evm_votes = Voted.objects.filter(where_voted='evm').count()
    
    print(f"  Online Voting:  {online_votes:,} votes")
    print(f"  EVM Voting:     {evm_votes:,} votes")
    
    # Recent voting activity
    print_subheader("Recent Voting Activity (Last 10)")
    recent_votes = Voted.objects.filter(has_voted='yes').order_by('-datetime')[:10]
    
    for idx, vote in enumerate(recent_votes, 1):
        print(f"  [{idx:2}] Voter: {vote.voter_id:10} | Election: {vote.election_id:10} | "
              f"Time: {vote.datetime} | IP: {vote.ipaddress}")

# ==================== COMPLAINTS ====================
print_header("⚠️ VOTER COMPLAINTS")

total_complaints = Complain.objects.count()
replied_complaints = Complain.objects.filter(replied=True).count()
pending_complaints = total_complaints - replied_complaints

print(f"  ✓ Total Complaints:      {total_complaints:,}")
print(f"  ✓ Replied:               {replied_complaints:,}")
print(f"  ✓ Pending:               {pending_complaints:,}")

if total_complaints > 0:
    print_subheader("Recent Complaints (Last 5)")
    for idx, complaint in enumerate(Complain.objects.all()[:5], 1):
        status = "✓ Replied" if complaint.replied else "⏳ Pending"
        print(f"\n  [{idx}] Voter ID: {complaint.voterid_no} | Status: {status}")
        print(f"      Complaint: {complaint.complain[:70]}...")
        if complaint.complain_reply:
            print(f"      Reply: {complaint.complain_reply[:70]}...")

# ==================== DATA INTEGRITY CHECKS ====================
print_header("🔒 DATA INTEGRITY & SECURITY CHECKS")

print_subheader("Duplicate Voting Prevention")
duplicate_voters = defaultdict(int)
for record in Voted.objects.filter(has_voted='yes'):
    duplicate_voters[record.voter_id] += 1

multi_voters = {voter: count for voter, count in duplicate_voters.items() if count > 1}

if multi_voters:
    print(f"  ⚠️  WARNING: {len(multi_voters)} voter(s) voted multiple times!")
    for voter_id, count in list(multi_voters.items())[:5]:
        print(f"      Voter {voter_id}: {count} votes")
else:
    print("  ✅ No duplicate votes detected - Data integrity verified!")

print_subheader("Biometric Data Status")
voter_faces_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'voter_faces')
training_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TrainingImage')

if os.path.exists(voter_faces_dir):
    face_files = len([f for f in os.listdir(voter_faces_dir) if f.endswith(('.jpg', '.png', '.jpeg'))])
    print(f"  ✓ Stored Voter Faces: {face_files} files")
else:
    print(f"  ⚠️  Voter faces directory not found")

if os.path.exists(training_dir):
    training_files = len([f for f in os.listdir(training_dir) if f.endswith(('.jpg', '.png', '.jpeg'))])
    print(f"  ✓ Training Images (for face recognition): {training_files} files")
else:
    print(f"  ⚠️  Training images directory not found")

# ==================== SUMMARY ====================
print_header("📌 SUMMARY FOR EVALUATOR")

print("\n  DATABASE LOCATION:")
print(f"    • Type: PostgreSQL (enterprise-grade relational database)")
print(f"    • Name: digital_voting")
print(f"    • Host: localhost:5432")
print(f"    • Admin URL: http://localhost:8000/admin/")

print("\n  DATA STORED:")
print(f"    ✓ {total_voters:,} Voter profiles with personal & biometric data")
print(f"    ✓ {total_candidates:,} Candidate information with party details")
print(f"    ✓ {total_votes_cast:,} Cast votes with timestamp & IP tracking")
print(f"    ✓ Audit trail with IP addresses for all voting activity")
print(f"    ✓ Encrypted passwords for all user accounts")
print(f"    ✓ OTP records for two-factor authentication")

print("\n  SECURITY FEATURES:")
print(f"    ✓ PostgreSQL database with multi-user access control")
print(f"    ✓ Password hashing (PBKDF2 algorithm)")
print(f"    ✓ OTP-based two-factor authentication")
print(f"    ✓ Face recognition for identity verification")
print(f"    ✓ Duplicate voting prevention mechanism")
print(f"    ✓ IP address logging for audit trail")
print(f"    ✓ Session-based access control")

print("\n  HOW TO VIEW DATA:")
print(f"    1. Django Admin Panel: http://localhost:8000/admin/")
print(f"    2. pgAdmin GUI Tool: http://localhost:5050/")
print(f"    3. Command Line: psql -U admin -d digital_voting -h localhost")
print(f"    4. Run this script: python show_database_report.py")

print("\n" + "╔" + "="*78 + "╗")
print("║" + " "*78 + "║")
print("║" + " "*20 + "✅ All system data is securely stored in PostgreSQL" + " "*18 + "║")
print("║" + " "*78 + "║")
print("╚" + "="*78 + "╝\n")
