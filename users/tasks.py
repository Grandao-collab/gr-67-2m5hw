from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_otp_mail(email, code):
    print("start")
    send_mail(
        "Регистрация в моем приложении",
        f"Ваш одноразовый код: {code}.",
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
    print("end")
    return "SENT!"

@shared_task
def delete_unactive_users():
    from users.models import CustomUser
    deleted = CustomUser.objects.filter(is_active=False).delete()
    return f"Deleted: {deleted}"
