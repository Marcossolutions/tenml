from django.core.mail import send_mail
from django.conf import settings
from django.dispatch import receiver, Signal
from django.utils.crypto import get_random_string
from django.utils import timezone

user_registered = Signal()

@receiver(user_registered)
def send_otp_email(sender, user, request, **kwargs):

    otp = get_random_string(length=6, allowed_chars='1234567890')
    print(otp)  

    otp_generation_time = timezone.now().isoformat()
    request.session['otp'] = otp
    request.session['otp_generation_time'] = otp_generation_time

    send_mail(
        'OTP Verification',
        f'Your OTP code is {otp}',
        settings.DEFAULT_FROM_EMAIL,
        [user['email']],
        fail_silently=False,
    )