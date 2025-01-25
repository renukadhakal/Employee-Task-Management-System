from django.core.mail import send_mail
from django.conf import settings

def send_registration_email(user_email, username, password):
    subject = 'Welcome to ETMS!'
    message = (
        f'Hi {username},\n\n'
        'You have been successfully onboarded to ETMS. Below are your login credentials:\n\n'
        f'Username: {username}\n'
        f'Password: {password}\n\n'
        'Please log in to your account and change your password immediately for security purposes.\n\n'
        'Best regards,\n'
        'The ETMS Team'
    )
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    send_mail(subject, message, email_from, recipient_list)