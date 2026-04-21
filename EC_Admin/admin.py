from django.contrib import admin
from .models import Voters, Candidates, Election, Votes, EC_Admins, Reports


@admin.register(Voters)
class VotersAdmin(admin.ModelAdmin):
    list_display = ['voterid_no', 'name', 'email', 'mobile_no', 'state', 'assembly']
    search_fields = ['voterid_no', 'name', 'email', 'state']
    list_filter = ['state', 'gender']


@admin.register(Candidates)
class CandidatesAdmin(admin.ModelAdmin):
    list_display = ['candidate_id', 'name', 'candidate_party', 'state', 'parliamentary', 'assembly']
    search_fields = ['candidate_id', 'name', 'state']
    list_filter = ['state', 'candidate_party']
    fieldsets = (
        ('Candidate Information', {
            'fields': ('candidate_id', 'name', 'father_name', 'gender', 'dateofbirth', 'mobile_no')
        }),
        ('Address Details', {
            'fields': ('address', 'state', 'pincode', 'parliamentary', 'assembly')
        }),
        ('Party & Documents', {
            'fields': ('candidate_party', 'candidate_image', 'party_image', 'affidavit')
        }),
    )


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ['election_id', 'election_type', 'state', 'start_date', 'status']
    search_fields = ['election_id', 'state']
    list_filter = ['status', 'election_type']
    fieldsets = (
        ('Election Information', {
            'fields': ('election_id', 'election_type', 'state', 'status')
        }),
        ('Start Details', {
            'fields': ('start_date', 'start_time')
        }),
        ('End Details', {
            'fields': ('end_date', 'end_time')
        }),
    )


@admin.register(Votes)
class VotesAdmin(admin.ModelAdmin):
    list_display = ['candidate_name', 'candidate_party', 'state', 'online_votes', 'evm_votes', 'total_votes']
    search_fields = ['candidate_name', 'state']
    list_filter = ['state', 'candidate_party']


@admin.register(Reports)
class ReportsAdmin(admin.ModelAdmin):
    list_display = ['election_id', 'state', 'constituency', 'electors_total', 'voters_total']
    search_fields = ['election_id', 'state']
    list_filter = ['state']


@admin.register(EC_Admins)
class EC_AdminsAdmin(admin.ModelAdmin):
    list_display = ['ecadmin_id', 'firstname', 'lastname', 'email', 'mobile_no']
    search_fields = ['ecadmin_id', 'firstname', 'lastname', 'email']
    list_filter = ['gender']