import threading
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_mail_in_thread(to_email,link_verification, username):
        nd = 'Verification Account On Game Store'
        html_message = render_to_string('user/verify_mail.html', {'link_verification': link_verification, 'username': username})
        plain_message = strip_tags(html_message)
        
        message = EmailMultiAlternatives(
            subject=nd,
            body=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[to_email],
        )
        message.attach_alternative(html_message, 'text/html')
        message.send()
        print("Email sent")
def send_mail_thread(to_mail, link_verification, username):
    threading.Thread(target=send_mail_in_thread, args=(to_mail,link_verification, username)).start()
