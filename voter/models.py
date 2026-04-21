from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from voter.utils import calculate_age

# Create your models here.
class Voter(models.Model):
    voterid_no = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    dateofbirth = models.DateField()
    address = models.TextField()
    mobile_no = models.CharField(max_length=15)
    email = models.EmailField(null=True, blank=True)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    parliamentary = models.CharField(max_length=100)
    assembly = models.CharField(max_length=100)
    voter_image = models.ImageField(upload_to='voters/')

    def clean(self):
        if calculate_age(self.dateofbirth) < 18:
            raise ValidationError({
                'dateofbirth': 'Voter must be at least 18 years old.'
            })

    def __str__(self):
        return self.name
    
class Voted(models.Model):
    election_id = models.CharField(max_length=50)
    voter_id = models.CharField(max_length=10)
    state = models.CharField(max_length=50)
    constituency = models.CharField(max_length=50)
    has_voted = models.CharField(max_length=3)
    where_voted = models.CharField(max_length=7, null=True)
    ipaddress = models.GenericIPAddressField(null=True)
    datetime = models.DateTimeField(null=True)


class VoteOTP(models.Model):
    """Store OTPs for vote confirmation (avoids SMTP issues)"""
    voter_id = models.CharField(max_length=10)
    election_id = models.CharField(max_length=50)
    otp_stage = models.CharField(max_length=20, choices=[
        ('vote_email', 'First OTP (vote confirmation)'),
        ('email', 'Second OTP (email confirmation)')
    ])
    otp_value = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at
    
    class Meta:
        ordering = ['-created_at']


class Complain(models.Model):
    voterid_no=models.CharField(max_length=10)
    complain=models.CharField(max_length=5000)
    complain_reply=models.CharField(max_length=5000, null=True)
    viewed=models.BooleanField(default=False)
    replied=models.BooleanField(default=False)