from django.contrib.auth import get_user_model

User = get_user_model()
username = 'admin'
email = 'admin@example.com'
password = 'admin123'

u = User.objects.filter(username=username).first()
if u:
    u.set_password(password)
    u.email = email
    u.is_superuser = True
    u.is_staff = True
    u.save()
    print('Updated existing superuser')
else:
    User.objects.create_superuser(username, email, password)
    print('Created superuser')
