# Secure E-Voting System (Django)

## 📌 Project Overview
This project is a secure online E-Voting System developed using the Django framework. It integrates face recognition and two-factor authentication (OTP) to ensure safe and reliable digital voting.

The system consists of two main roles: **Admin** and **Voter**. The admin (election authority) manages voters and elections, while voters can securely log in and cast their votes.

---

## 🚀 Features
- User Registration & Login  
- Admin-controlled voter registration  
- OTP (Two-Factor Authentication)  
- Facial Recognition Authentication  
- Secure Voting System  
- Candidate Information Display  
- One Vote per Voter per Election  
- Admin Dashboard  

---

## 🛠️ Technologies Used
- Python  
- Django  
- HTML, CSS, JavaScript  
- SQLite  

---

## ▶️ How to Run
1. Clone the repository  
2. Install dependencies: pip install -r requirements.txt
3. Run the server: python manage.py runserver
4. Open browser and go to: http://127.0.0.1:8000/


---

## ⚙️ How It Works
- The admin first registers voters by assigning a unique Voter ID.  
- Voters complete registration using their details and create a password.  
- Voters log in using their Voter ID and password.  
- The system displays candidates with their background information.  
- During voting, the voter selects a candidate.  
- The system performs face recognition using a webcam or front camera.  
- If the face matches, OTP verification is performed.  
- Once authentication is successful, the vote is securely submitted.  
- Each voter can vote only once per election.  

---

## 📌 Note
This project is based on an existing implementation and has been modified and enhanced for learning purposes. Additional features such as face recognition and OTP authentication have been integrated and improved.

---

## 🙏 Acknowledgement
This project uses third-party libraries such as face recognition tools and other open-source resources. Credits belong to their respective owners.

---

## 👨‍💻 Author
Gajanand Teli