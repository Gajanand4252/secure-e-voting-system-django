from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
import logging
from django.conf import settings
from django.utils import timezone
from Digital_Voting.settings import BASE_DIR
from EC_Admin.models import Voters, Candidates, Election, Votes, Reports
from .models import Voted, Complain, VoteOTP
import os
import requests
import datetime 
import math
import random
import base64
import io
from datetime import date
import numpy as np
from PIL import Image
import cv2  

from django.http import JsonResponse
import secrets
import time
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import User

OTP_EXPIRY_SECONDS = 300  # 5 minutes

logger = logging.getLogger(__name__)

def calculate_age(dob):
    today = date.today()
    return today.year - dob.year - (
        (today.month, today.day) < (dob.month, dob.day)
    )

def register_vid(request):
    if request.method == 'POST':
        voterid = request.POST.get('vid')

        if User.objects.filter(username=voterid).exists():
            messages.info(request, 'Voter already registered')
            return render(request, 'registervid.html')

        if not Voters.objects.filter(voterid_no=voterid).exists():
            messages.info(request, 'Invalid Voter ID')
            return render(request, 'registervid.html')

        voter = Voters.objects.get(voterid_no=voterid)
        age = calculate_age(voter.dateofbirth)

        if age < 18:
            messages.error(request, 'You are not eligible to vote. Age must be 18 or above.')
            return render(request, 'registervid.html')

        if not voter.email:
            messages.info(request, 'No email found. Please contact administrator.')
            return render(request, 'registervid.html')

        # Generate secure OTP
        otp = ''.join(secrets.choice('0123456789') for _ in range(6))

        # Store OTP in session
        request.session['email_otp'] = otp
        request.session['otp_time'] = int(time.time())
        request.session['voterid'] = voterid

        try:
            send_mail(
                'OTP from Digital Voting System',
                f'Your OTP for registration is: {otp}\nValid for 5 minutes.',
                settings.EMAIL_HOST_USER,
                [voter.email],
                fail_silently=False
            )

            masked = voter.email[:3] + '*****' + voter.email[-13:]
            messages.success(request, 'OTP sent to your registered email')
            return render(request, 'otp.html', {'email': masked})

        except Exception as e:
            messages.error(request, 'Failed to send OTP. Please try again.')
            print("Email Error:", e)
            return render(request, 'registervid.html')

    return render(request, 'registervid.html')



def otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')

        session_otp = request.session.get('email_otp')
        otp_time = request.session.get('otp_time')
        voterid = request.session.get('voterid')

        if not session_otp or not otp_time:
            messages.error(request, 'OTP session expired. Please retry.')
            return render(request, 'registervid.html')

        if int(time.time()) - otp_time > OTP_EXPIRY_SECONDS:
            messages.error(request, 'OTP expired. Please request a new one.')
            return render(request, 'registervid.html')

        if user_otp != session_otp:
            messages.error(request, 'Invalid OTP')
            return render(request, 'otp.html')

        voter = Voters.objects.get(voterid_no=voterid)

        # Clear OTP from session
        del request.session['email_otp']
        del request.session['otp_time']
        del request.session['voterid']

        return render(request, 'register.html', {
            'voterid_no': voter.voterid_no,
            'name': voter.name,
            'father_name': voter.father_name,
            'gender': voter.gender,
            'dateofbirth': voter.dateofbirth,
            'address': voter.address,
            'mobile_no': voter.mobile_no,
            'state': voter.state,
            'pincode': voter.pincode,
            'parliamentary': voter.parliamentary,
            'assembly': voter.assembly,
            'voter_image': voter.voter_image,
        })

    return render(request, 'otp.html')



def register(request):
    if (request.method == 'POST'):
        voter_id = request.POST.get('v_id')
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        facefile = request.POST.get('facefile')  # Get the base64 face image
        
        if not facefile:
            messages.error(request, 'Please capture your face image before registering.')
            v = Voters.objects.get(voterid_no=voter_id)
            return render(request, 'pages/register.html', {'voterid_no': v.voterid_no, 'name': v.name,
                                                            'father_name': v.father_name, 'gender': v.gender,
                                                            'dateofbirth': v.dateofbirth, 'address': v.address,
                                                            'mobile_no': v.mobile_no, 'state': v.state,
                                                            'pincode': v.pincode, 'parliamentary': v.parliamentary,
                                                            'assembly': v.assembly, 'voter_image': v.voter_image})
        
        v = Voters.objects.get(voterid_no=voter_id)
        Id = str(v.id)
        
        # Process and save face image from base64
        try:
            # Extract base64 data from data URL
            if facefile.startswith('data:image'):
                facefile = facefile.split(',')[1]
            
            # Decode base64 image
            face_image_data = base64.b64decode(facefile)
            face_image = Image.open(io.BytesIO(face_image_data))
            
            # Convert to RGB if necessary
            if face_image.mode != 'RGB':
                face_image = face_image.convert('RGB')
            
            # Ensure voter_faces directory exists
            voter_faces_dir = os.path.join(str(BASE_DIR), 'media', 'voter_faces')
            os.makedirs(voter_faces_dir, exist_ok=True)
            face_path = os.path.join(voter_faces_dir, f'{voter_id}.jpg')
            face_image.save(face_path)
            
            # Convert saved image to grayscale for LBPH training
            face_image_gray = face_image.convert('L')
            
            # Save training image for LBPH
            training_image_path = os.path.join(str(BASE_DIR), 'TrainingImage', f'{voter_id}.{Id}.1.jpg')
            face_image_gray.save(training_image_path)
            
        except Exception as e:
            messages.error(request, f'Error processing face image: {str(e)}')
            return render(request, 'pages/register.html', {'voterid_no': v.voterid_no, 'name': v.name,
                                                            'father_name': v.father_name, 'gender': v.gender,
                                                            'dateofbirth': v.dateofbirth, 'address': v.address,
                                                            'mobile_no': v.mobile_no, 'state': v.state,
                                                            'pincode': v.pincode, 'parliamentary': v.parliamentary,
                                                            'assembly': v.assembly, 'voter_image': v.voter_image})
        
        # Train the recognizer using training images
        recognizer = cv2.face.LBPHFaceRecognizer_create()

        def getImagesAndLabels(path):
            imagePaths = [os.path.join(path, f) for f in os.listdir(path) if f != ".gitkeep"]
            faces = []
            Ids = []
            for imagePath in imagePaths:
                pilImage = Image.open(imagePath).convert('L')
                imageNp = np.array(pilImage, 'uint8')
                Id = int(os.path.split(imagePath)[-1].split('.')[1])
                faces.append(imageNp)
                Ids.append(Id)
            return faces, Ids
        
        faces, Id = getImagesAndLabels(str(BASE_DIR) + "/TrainingImage/")
        recognizer.train(faces, np.array(Id))
        recognizer.save(str(BASE_DIR) + "/TrainingImageLabel/Trainner.yml")
        
        if password1 == password2:
            add_user = User.objects.create_user(username=voter_id, password=password1, email=email)
            add_user.save()
            # Save email to Voters model
            v.email = email
            v.save()
            messages.info(request, 'Voter Registered')
            return redirect("/")


@login_required(login_url='home')
def vhome(request):
    vhome.username=request.session['v_id']
    v = Voters.objects.get(voterid_no=vhome.username)
    vhome.image=v.voter_image
    return render(request,'voter/vhome.html',{'username':vhome.username,'image':vhome.image})


@login_required(login_url='home')
def vprocess(request):
    v_id = request.session['v_id']
    vdetail = Voters.objects.get(voterid_no=v_id)
    username = v_id
    image = vdetail.voter_image
    return render(request,'voter/votingprocess.html',{'username':username,'image':image})


@login_required(login_url='home')
def vprofile(request):
    v_id = request.session['v_id']
    v = Voters.objects.get(voterid_no=v_id)
    vemail = User.objects.get(username=v_id)
    username = v_id
    image = v.voter_image
    return render(request, 'voter/voter profile.html', {'voterid_no': v.voterid_no, 'name': v.name,
                                                  'father_name': v.father_name, 'gender': v.gender,
                                                  'dateofbirth': v.dateofbirth, 'address': v.address,
                                                  'mobile_no': v.mobile_no, 'state': v.state,
                                                  'pincode': v.pincode, 'parliamentary': v.parliamentary,
                                                  'assembly': v.assembly, 'voter_image': v.voter_image,
                                                  'email': vemail.email,'username':username,'image':image})


@login_required(login_url='home')
def vchangepassword(request):
    v_id = request.session['v_id']
    vdetail = Voters.objects.get(voterid_no=v_id)
    username = v_id
    image = vdetail.voter_image
    return render(request, 'voter/vchangepassword.html',{'username':username,'image':image})


@login_required(login_url='home')
def vchange_password(request):
    if request.method == "POST":
        v_id = request.session['v_id']
        vdetail = Voters.objects.get(voterid_no=v_id)
        username = v_id
        image = vdetail.voter_image
        oldpass = request.POST['oldpass']
        newpass = request.POST['password1']
        newpass2 = request.POST['password2']
        u=auth.authenticate(username=v_id,password=oldpass)
        if u is not None:
            u=User.objects.get(username=v_id)
            if oldpass!=newpass:
                if newpass == newpass2:
                    u.set_password(newpass)
                    u.save()
                    messages.info(request, 'Password Changed')
                    return render(request, 'voter/vchangepassword.html',{'username':username,'image':image})
            else:
                messages.info(request, 'New password is same as old password')
                return render(request, 'voter/vchangepassword.html',{'username':username,'image':image})
        else:
            messages.info(request, 'Old Password not matching')
            return render(request, 'voter/vchangepassword.html',{'username':username,'image':image})


@login_required(login_url='home')
def vviewcandidate(request):
    v_id = request.session['v_id']
    vdetail = Voters.objects.get(voterid_no=v_id)
    username = v_id
    image = vdetail.voter_image
    return render(request, 'voter/view candidate.html',{'username':username,'image':image})


@login_required(login_url='home')
def vview_candidate(request):
    v_id = request.session['v_id']
    vdetail = Voters.objects.get(voterid_no=v_id)
    username = v_id
    image = vdetail.voter_image
    if request.method == 'POST':
        state = request.POST.get('states', '').strip()
        parliamentary = request.POST.get('ParliamentaryConstituency', '').strip()
        assembly = request.POST.get('AssemblyConstituency', '').strip()
        # Prefer parliamentary when provided, otherwise use assembly
        if parliamentary:
            candidates = Candidates.objects.filter(state=state, parliamentary=parliamentary)
            if candidates:
                return render(request, 'voter/view candidate.html', {'constituency': parliamentary, 'candidates': candidates, 'username': username, 'image': image})
            else:
                messages.info(request, 'No Candidate Found')
                return render(request, 'voter/view candidate.html', {'username': username, 'image': image})
        elif assembly:
            candidates = Candidates.objects.filter(state=state, assembly=assembly)
            if candidates:
                return render(request, 'voter/view candidate.html', {'constituency': assembly, 'candidates': candidates, 'username': username, 'image': image})
            else:
                messages.info(request, 'No Candidate Found')
                return render(request, 'voter/view candidate.html', {'username': username, 'image': image})
        else:
            messages.info(request, 'Please enter a Parliamentary or Assembly constituency to filter')
            return render(request, 'voter/view candidate.html', {'username': username, 'image': image})


@login_required(login_url='home')
def velection(request):
    v_id = request.session['v_id']
    vdetail = Voters.objects.get(voterid_no=v_id)
    username = v_id
    image = vdetail.voter_image
    
    status = 'active'
    # Find active elections for voter's state
    active_elections = Election.objects.filter(state=vdetail.state, status=status).order_by('start_date', 'start_time')
    if not active_elections.exists():
        messages.info(request, 'No Elections Running')
        return render(request, 'voter/vnoelection.html', {'username': username, 'image': image})

    # pick the first active election (if multiple exist)
    election = active_elections.first()
    # Store election details in session for use in vote view
    request.session['election_id'] = election.election_id
    request.session['election_type'] = election.election_type
    request.session['election_state'] = election.state
    now = timezone.localtime()
    today = now.date()
    now_time = now.time()

    # Check if today's date is within election dates
    if election.start_date <= today <= election.end_date:
        # If election spans multiple days, it's running now.
        # For start/end boundary days, also check times.
        starts_today = (today == election.start_date)
        ends_today = (today == election.end_date)

        time_ok = False
        if starts_today and ends_today:
            # Single-day election: ensure current time is between start and end
            time_ok = (election.start_time <= now_time <= election.end_time)
        elif starts_today:
            time_ok = (now_time >= election.start_time)
        elif ends_today:
            time_ok = (now_time <= election.end_time)
        else:
            time_ok = True

        if time_ok:
            if election.election_type == 'PC-GENERAL':
                vpc = vdetail.parliamentary
                candidates = Candidates.objects.filter(state=vdetail.state, parliamentary=vpc)
                return render(request, 'voter/velection.html', {'candidate': candidates, 'username': username, 'image': image})
            elif election.election_type == 'AC-GENERAL':
                vac = vdetail.assembly
                candidates = Candidates.objects.filter(state=vdetail.state, assembly=vac)
                return render(request, 'voter/velection.html', {'candidate': candidates, 'username': username, 'image': image})
        else:
            messages.info(request, 'No Elections Running')
            return render(request, 'voter/vnoelection.html', {'username': username, 'image': image})
    else:
        messages.info(request, 'No Elections Running')
        return render(request, 'voter/vnoelection.html', {'username': username, 'image': image})


@login_required(login_url='home')
def vote(request):
    if request.method == "POST":
        v_id = request.session['v_id']
        vdetail = Voters.objects.get(voterid_no=v_id)
        username = v_id
        image = vdetail.voter_image
        # Get election ID from session
        election_id = request.session.get('election_id')
        if not election_id:
            messages.error(request, 'No election selected. Please go back to election view.')
            return redirect('velection')
        
        # Check if voter has already voted in this specific election
        existing_vote = Voted.objects.filter(
            election_id=election_id,
            voter_id=v_id,
            has_voted='yes'
        ).first()
        
        if existing_vote:
            messages.info(request, 'Already Voted')
            return render(request, 'voter/votesub.html',{'username':username,'image':image})
        
        # Get or create the Voted record for this voter and election
        voted_record, created = Voted.objects.get_or_create(
            election_id=election_id,
            voter_id=v_id,
            defaults={'has_voted': 'no'}
        )
        
        # Store voted record ID in session for later use
        request.session['voted_record_id'] = voted_record.id
        
        vidofv = Voters.objects.get(voterid_no=v_id)
        detectuserid = str(vidofv.id)
        # Get the captured face image from form
        faceimage = request.POST.get('faceimage')
        if not faceimage:
            messages.error(request, 'No face image captured')
            return redirect('velection')
        
        try:
            # Extract base64 data from data URL
            if faceimage.startswith('data:image'):
                faceimage = faceimage.split(',')[1]
            
            # Decode base64 image
            face_image_data = base64.b64decode(faceimage)
            voting_face_img = Image.open(io.BytesIO(face_image_data))
            
            # Convert to grayscale for comparison
            voting_face_gray = voting_face_img.convert('L')
            voting_face_array = np.array(voting_face_gray)
                
        except Exception as e:
            messages.error(request, f'Error processing face image: {str(e)}')
            return redirect('velection')
        
        # Load reference face for comparison
        voter_faces_dir = os.path.join(str(BASE_DIR), 'media', 'voter_faces')
        ref_face_path = os.path.join(voter_faces_dir, f'{v_id}.jpg')
        if not os.path.exists(ref_face_path):
            messages.error(request, 'No registered face found. Please register again.')
            return redirect('velection')
        
        ref_face = cv2.imread(ref_face_path, cv2.IMREAD_GRAYSCALE)
        if ref_face is None:
            messages.error(request, 'Error loading registered face.')
            return redirect('velection')
        
        # Resize voting face to match reference face dimensions
        voting_face_resized = cv2.resize(voting_face_array, (ref_face.shape[1], ref_face.shape[0]))
        
        # Apply histogram equalization for better comparison (reduces lighting differences)
        ref_face_eq = cv2.equalizeHist(ref_face)
        voting_face_eq = cv2.equalizeHist(voting_face_resized)
        
        # Method 1: Histogram comparison (measures distribution similarity)
        hist_ref = cv2.calcHist([ref_face_eq], [0], None, [256], [0, 256])
        hist_voting = cv2.calcHist([voting_face_eq], [0], None, [256], [0, 256])
        
        # Normalize histograms
        cv2.normalize(hist_ref, hist_ref)
        cv2.normalize(hist_voting, hist_voting)
        
        # Compare using multiple methods for more reliable results
        bhatt_dist = cv2.compareHist(hist_ref, hist_voting, cv2.HISTCMP_BHATTACHARYYA)
        histogram_confidence = max(0, 100 - (bhatt_dist * 100))
        
        # Method 2: Structural Similarity using Mean Squared Error
        mse = cv2.matchTemplate(voting_face_eq, ref_face_eq, cv2.TM_SQDIFF_NORMED)
        mse_confidence = max(0, 100 - (float(mse) * 100))
        
        # Method 3: Template matching (finds similarity)
        result = cv2.matchTemplate(voting_face_eq, ref_face_eq, cv2.TM_CCOEFF_NORMED)
        template_confidence = float(result) * 100 if result.size > 0 else 0
        
        # Average all methods for a more robust score
        face_match_confidence = (histogram_confidence + mse_confidence + max(0, template_confidence)) / 3
        
        logger.info(f"Face matching scores - Histogram: {histogram_confidence:.1f}%, MSE: {mse_confidence:.1f}%, Template: {template_confidence:.1f}%, Average: {face_match_confidence:.1f}%")
        print(f"\n{'='*60}")
        print(f"FACE MATCHING ANALYSIS FOR VOTER: {v_id}")
        print(f"{'='*60}")
        print(f"Histogram Confidence:  {histogram_confidence:.1f}%")
        print(f"MSE Confidence:        {mse_confidence:.1f}%")
        print(f"Template Confidence:   {template_confidence:.1f}%")
        print(f"Average Confidence:    {face_match_confidence:.1f}%")
        print(f"Threshold:             50%")
        print(f"Match Result:          {'✅ PASSED' if face_match_confidence > 50 else '❌ FAILED'}")
        print(f"{'='*60}\n")
        
        # Check if face matches with lowered threshold (50% instead of 70%)
        if face_match_confidence > 50:  # Lowered from 70% to 50% for better reliability
            candidate_id = request.POST.get('can')
            if not candidate_id:
                messages.error(request, 'No candidate selected. Please select a candidate.')
                return redirect('velection')
            # Store candidate ID in session
            request.session['vote_candidate_id'] = candidate_id
            v_user = User.objects.get(username=v_id)
            vemail = v_user.email
            
            # Generate OTP for vote confirmation
            string = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            length = len(string)
            email_otp = ""
            for i in range(6):
                email_otp += string[math.floor(random.random() * length)]
            
            # Store OTP in VoteOTP model (database) with 5-minute expiry
            from django.utils import timezone
            from datetime import timedelta
            otp_expiry = timezone.now() + timedelta(seconds=OTP_EXPIRY_SECONDS)
            
            # Create or update OTP in database
            vote_otp = VoteOTP.objects.create(
                voter_id=v_id,
                election_id=election_id,
                otp_stage='vote_email',
                otp_value=email_otp,
                expires_at=otp_expiry
            )
            
            # Also store in session as backup
            request.session['vote_email_otp'] = email_otp
            request.session.save()
            
            # Try to send OTP via email, but don't fail if it doesn't work
            try:
                result = send_mail(
                    'OTP from Digital Voting',
                    f'Your 6-digit OTP for vote confirmation is: {email_otp}\nValid for 5 minutes.',
                    settings.EMAIL_HOST_USER,
                    [vemail],
                    fail_silently=False
                )
                logger.info(f"vote: send_mail result={result} to {vemail}")
            except Exception as e:
                logger.warning(f'vote: Exception while sending email OTP: {str(e)}. OTP stored in database.')
                # OTP is still stored in database, so voting can proceed
            
            messages.info(request, 'OTP has been sent to your registered email')
            emailstart = vemail[0:3]
            emailend = vemail[-13:]
            emailid = emailstart + '*****' + emailend
            return render(request, 'voter/voteotp.html', {'username': username, 'image': image, 'email': emailid})
        else:
            messages.error(request, f'Face not matched. Your face match confidence is {face_match_confidence:.1f}%. Required minimum: 50%. Please ensure proper lighting, clear face visibility, and correct positioning before trying again.')
            # Fetch candidates for re-display
            election_type = request.session.get('election_type')
            if election_type == 'PC-GENERAL':
                candidates = Candidates.objects.filter(state=vdetail.state, parliamentary=vdetail.parliamentary)
            else:
                candidates = Candidates.objects.filter(state=vdetail.state, assembly=vdetail.assembly)
            return render(request, 'voter/velection.html',{'candidate':candidates,'username':username,'image':image})


@login_required(login_url='home')
def subvoteotp(request):
    if (request.method == "POST"):
        userotp = request.POST.get('otp', '').strip()
        v_id = request.session.get('v_id')
        election_id = request.session.get('election_id')
        
        # First try to validate OTP from database (VoteOTP model)
        db_otp_valid = False
        if v_id and election_id:
            try:
                # Check for valid OTP in database
                vote_otp = VoteOTP.objects.filter(
                    voter_id=v_id,
                    election_id=election_id,
                    otp_stage='vote_email',
                    otp_value=userotp,
                    is_used=False
                ).first()
                
                if vote_otp and vote_otp.is_valid():
                    db_otp_valid = True
                    vote_otp.is_used = True
                    vote_otp.save()
                    logger.info(f"subvoteotp: OTP validated from database for voter {v_id}")
            except Exception as e:
                logger.warning(f"subvoteotp: Error checking database OTP: {str(e)}")
        
        # Fall back to session OTP if database check fails
        stored_email_otp = request.session.get('vote_email_otp')
        session_otp_valid = stored_email_otp and stored_email_otp == userotp
        
        logger.info(f"subvoteotp: User input OTP='{userotp}', DB OTP valid={db_otp_valid}, Session OTP valid={session_otp_valid}")
        print(f"subvoteotp: User input OTP='{userotp}', DB OTP valid={db_otp_valid}, Session OTP valid={session_otp_valid}")
        
        if db_otp_valid or session_otp_valid:
            # OTP verified — complete the vote
            vdetail = Voters.objects.get(voterid_no=v_id)
            username = v_id
            image = vdetail.voter_image

            # Retrieve candidate and election info from session
            candidate_id = request.session.get('vote_candidate_id')
            voted_record_id = request.session.get('voted_record_id')
            if not candidate_id or not election_id or not voted_record_id:
                messages.error(request, 'Session expired. Please vote again.')
                return redirect('velection')

            # Update vote counts and voted record
            voted_record = Voted.objects.get(id=voted_record_id)
            try:
                votecan = Votes.objects.get(election_id=election_id, candidate_id=candidate_id)
            except Votes.DoesNotExist:
                logger.error(f"subvoteotp: Votes record not found for election_id={election_id}, candidate_id={candidate_id}")
                print(f"subvoteotp: Votes record not found for election_id={election_id}, candidate_id={candidate_id}")
                messages.error(request, 'Vote record not found. Please contact administrator.')
                return redirect('velection')
            votecan.online_votes += 1
            votecan.save()
            voted_record.has_voted = 'yes'
            voted_record.where_voted = 'online'
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ipaddress = x_forwarded_for.split(',')[-1].strip()
            else:
                ipaddress = request.META.get('REMOTE_ADDR')
            voted_record.ipaddress = ipaddress
            voted_record.datetime = timezone.now()
            voted_record.save()

            # Clear related session keys
            for key in ('email_otp', 'vote_email_otp', 'vote_candidate_id', 'voted_record_id'):
                if key in request.session:
                    del request.session[key]

            messages.info(request, 'Vote submitted to ')
            return render(request, 'voter/votesub.html', {'votesub': votecan.candidate_name, 'username': username, 'image': image})
        else:
            # OTP mismatch - render voteotp.html again to let user retry
            vdetail = Voters.objects.get(voterid_no=v_id) if v_id else None
            username = v_id
            image = vdetail.voter_image if vdetail else None
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, 'voter/voteotp.html',{'username':username,'image':image})


@login_required(login_url='home')   
def subvoteemailotp(request):
    if request.method=="POST":
        v_id = request.session['v_id']
        vdetail = Voters.objects.get(voterid_no=v_id)
        username = v_id
        image = vdetail.voter_image
        emailotp = request.POST.get('emailotp', '').strip()
        # Retrieve OTP from session
        stored_email_otp = request.session.get('email_otp')
        logger.info(f"subvoteemailotp: User input OTP='{emailotp}', Stored OTP='{stored_email_otp}'")
        # Print to stdout so dev server shows it regardless of logger config
        print(f"subvoteemailotp: User input OTP='{emailotp}', Stored OTP='{stored_email_otp}'")
        if stored_email_otp and stored_email_otp == emailotp:
            # Retrieve candidate ID and election info from session
            candidate_id = request.session.get('vote_candidate_id')
            election_id = request.session.get('election_id')
            voted_record_id = request.session.get('voted_record_id')
            if not candidate_id or not election_id or not voted_record_id:
                messages.error(request, 'Session expired. Please vote again.')
                return render(request, 'voter/voteemailotp.html', {'username': username, 'image': image})
            
            # Get the voted record and vote record from database
            voted_record = Voted.objects.get(id=voted_record_id)
            votecan = Votes.objects.get(election_id=election_id, candidate_id=candidate_id)
            votecan.online_votes += 1
            votecan.save()
            voted_record.has_voted = 'yes'
            voted_record.where_voted = 'online'
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ipaddress = x_forwarded_for.split(',')[-1].strip()
            else:
                ipaddress = request.META.get('REMOTE_ADDR')
            voted_record.ipaddress = ipaddress
            voted_record.datetime = timezone.now()
            voted_record.save()
            # Clear OTPs and candidate from session after successful verification
            if 'email_otp' in request.session:
                del request.session['email_otp']
            if 'vote_email_otp' in request.session:
                del request.session['vote_email_otp']
            if 'vote_candidate_id' in request.session:
                del request.session['vote_candidate_id']
            messages.info(request, 'Vote submitted to ')
            return render(request, 'voter/votesub.html', {'votesub': votecan.candidate_name,'username':username,'image':image})
        else:
            messages.info(request, 'Invalid OTP')
            return render(request, 'voter/voteemailotp.html',{'username':username,'image':image})


@login_required(login_url='home')
def vviewresult(request):
    v_id = request.session['v_id']
    vdetail = Voters.objects.get(voterid_no=v_id)
    username = v_id
    image = vdetail.voter_image
    elections = Election.objects.all()
    return render(request, 'voter/viewresult.html', {'elections': elections,'username':username,'image':image})


@login_required(login_url='home')
def debug_session(request):
    # Return current session keys for debugging (temporary)
    data = {k: (str(v) if not isinstance(v, bytes) else v.decode('utf-8')) for k, v in request.session.items()}
    return JsonResponse({'session': data})


@login_required(login_url='home')
def vview_result(request):
    v_id = request.session['v_id']
    vdetail = Voters.objects.get(voterid_no=v_id)
    username = v_id
    image = vdetail.voter_image
    if request.method=="POST":
        election_id = request.POST['e_id']
        resulttype = request.POST['resulttype']
        e=Election.objects.get(election_id=election_id)
        estate=e.state
        if resulttype=="partywise":
            result = Votes.objects.filter(election_id=election_id)
            v=Votes.objects.filter(election_id=election_id)
            parties=[]
            for k in v:
                if k.candidate_party not in parties:
                    parties.append(k.candidate_party)
            final={}
            for i in parties:
                c=sum(1 for vote in v if vote.candidate_party==i)
                final.update({i:c})
            par=[]
            won=[]
            for k,v_count in final.items():
                par.append(k)
                won.append(v_count)
            parwon=zip(par,won)
            total=0
            for i in won:
                total+=i
            return render(request, 'voter/viewpartywise.html', {'total':total,'parwon':parwon,'electionid': election_id,'state':estate,'username':username,'image':image})
        elif resulttype=="constituencywise":
            # Removed constituency filtering as field was removed from Votes model
            return render(request, 'voter/viewresultconwise.html', {'electionid':election_id,'state':estate,'constituency':[],'username':username,'image':image})


@login_required(login_url='home')
def vview_result_filter(request):
    v_id = request.session['v_id']
    vdetail = Voters.objects.get(voterid_no=v_id)
    username = v_id
    image = vdetail.voter_image
    if request.method=="POST":
        election_id = request.POST['e_id']
        e=Election.objects.get(election_id=election_id)
        estate=e.state
        result = Votes.objects.filter(election_id=election_id)
        # Removed constituency filtering as field was removed from Votes model
        constituencies=[]
        totalvotes=0
        totalonline=0
        totalevm=0
        for i in result:
            totalvotes+=i.total_votes
            totalonline+=i.online_votes
            totalevm+=i.evm_votes
        perofvotes=[]
        for i in result:
            # Avoid division by zero when no votes have been cast
            if totalvotes > 0:
                per=(i.total_votes/totalvotes)*100
                percentage=float("{:.2f}".format(per))
            else:
                percentage=0.0
            perofvotes.append(percentage)
        finalresult=zip(result,perofvotes)
        return render(request, 'voter/viewresultconwise.html', {'totalonline':totalonline,'totalevm':totalevm,'totalvotes':totalvotes,'result':finalresult,'electionid':election_id,'state':estate,'constituency':[],'username':username,'image':image})


@login_required(login_url='home')
def vviewreport(request):
    v_id = request.session['v_id']
    vdetail = Voters.objects.get(voterid_no=v_id)
    username = v_id
    image = vdetail.voter_image
    elections = Election.objects.all()
    return render(request, 'voter/viewreport.html', {'elections': elections,'username':username,'image':image})


@login_required(login_url='home')
def vview_report(request):
    v_id = request.session['v_id']
    vdetail = Voters.objects.get(voterid_no=v_id)
    username = v_id
    image = vdetail.voter_image
    election_id = request.POST['e_id']
    # No longer filtering by constituency field
    report = Reports.objects.filter(election_id=election_id)
    elections = Election.objects.all()
    return render(request, 'voter/viewreport.html', {'report': report, 'elections':elections,'username':username,'image':image})


@login_required(login_url='home')
def vcomplain(request):
    v_id = request.session['v_id']
    vdetail = Voters.objects.get(voterid_no=v_id)
    username = v_id
    image = vdetail.voter_image
    complain=Complain.objects.filter(voterid_no=v_id,viewed=True,replied=True)
    return render(request, 'voter/vcomplain.html',{'voterid_no': v_id, 'reply':complain,'username':username,'image':image})


@login_required(login_url='home')
def submitcomplain(request):
    if (request.method == 'POST'):
        v_id = request.session['v_id']
        vdetail = Voters.objects.get(voterid_no=v_id)
        username = v_id
        image = vdetail.voter_image
        complain = request.POST['complain']
        addcomplain = Complain(voterid_no=v_id, complain=complain)
        addcomplain.save()
        messages.info(request, 'complain submitted')
        return render(request, 'voter/vcomplain.html',{'username':username,'image':image})
