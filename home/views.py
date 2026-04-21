from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.conf import settings
from django.core.mail import send_mail
from EC_Admin.models import Voters
import requests

# Create your views here.
def home(request):
    return render(request, 'index.html')


def login(request):
    if (request.method == 'POST'):
        username = request.POST['username']
        password = request.POST['password']
        # Default to voter login (admin removed from public login)
        loginas = request.POST.get('loginas', 'voter')
        
        # Only voter login is available
        if loginas == "voter":
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_superuser == False:
                auth.login(request, user)
                request.session['v_id'] = username
                return redirect('vhome')
            else:
                messages.info(request, 'Invalid Credentials')
                return render(request, 'index.html')
        else:
            # Reject any non-voter login attempts
            messages.info(request, 'Only voter login is available. Please use Django admin for administrator access.')
            return render(request, 'index.html')


def registervidpage(request):
    return render(request, 'registervid.html')


def forgotpassword(request):
    return render(request, 'forgotpassword.html')


def forgot_password(request):
    if request.method == "POST":
        vid = request.POST.get('vid')
        voter = User.objects.filter(username=vid).first()
        if not voter:
            messages.info(request, 'Invalid Voter ID')
            return render(request, 'forgotpassword.html')
        v = Voters.objects.filter(voterid_no=vid).first()
        if not v:
            messages.info(request, 'Invalid Voter ID')
            return render(request, 'forgotpassword.html')
        # Generate email OTP for password reset
        import random, math
        string = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        length = len(string)
        email_otp = ""
        for i in range(6):
            email_otp += string[math.floor(random.random() * length)]
        request.session['reset_email_otp'] = email_otp
        request.session['reset_voter_id'] = vid
        
        # Print OTP to console for development
        print(f"\n{'='*60}")
        print(f"PASSWORD RESET OTP FOR VOTER: {vid}")
        print(f"OTP: {email_otp}")
        print(f"Email: {voter.email}")
        print(f"{'='*60}\n")
        
        # Send OTP via email
        try:
            result = send_mail(
                'Password Reset OTP - Digital Voting',
                f'Your OTP for password reset is: {email_otp}\nValid for 5 minutes.',
                settings.EMAIL_HOST_USER,
                [voter.email],
                fail_silently=False
            )
            messages.info(request, 'OTP has been sent to your registered email')
            emailstart = voter.email[0:3]
            emailend = voter.email[-13:]
            emailid = emailstart + '*****' + emailend
            return render(request, 'forgotpassotp.html', {'email': emailid})
        except Exception as e:
            print(f"Email sending error: {str(e)}")
            # OTP is still stored in session, proceed to verification
            messages.info(request, 'OTP has been generated (check console for development)')
            emailstart = voter.email[0:3]
            emailend = voter.email[-13:]
            emailid = emailstart + '*****' + emailend
            return render(request, 'forgotpassotp.html', {'email': emailid})


def forgotpassotp(request):
    if (request.method == "POST"):
        userotp = request.POST['otp']
        reset_otp = request.session.get('reset_email_otp', '')
        if reset_otp == userotp:
            return render(request, 'newpassword.html')
        messages.info(request, 'Invalid OTP')
        return render(request, 'forgotpassotp.html')


def setnewpassword(request):
    if request.method == "POST":
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            vid = request.session.get('reset_voter_id')
            if not vid:
                messages.info(request, 'Session expired')
                return render(request, 'forgotpassword.html')
            u = User.objects.filter(username=vid).first()
            if not u:
                messages.info(request, 'Invalid Voter ID')
                return render(request, 'forgotpassword.html')
            u.set_password(password1)
            u.save()
            messages.info(request, 'New password updated')
            return render(request, 'index.html')


def logout(request):
    auth.logout(request)
    return redirect('/')
