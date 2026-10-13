from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


@shared_task
def send_otp_mail(email, code):
    """SMTP example: отправка одноразового кода пользователю."""
    send_mail(
        "Регистрация в моем приложении",
        f"Ваш одноразовый код: {code}.",
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
    return "SENT!"


@shared_task
def save_users_snapshot():
    """Delay() example: сохраняем список email пользователей в Redis-кэш."""
    from users.models import CustomUser

    emails = list(CustomUser.objects.values_list("email", flat=True))
    cache.set("users_snapshot", {"emails": emails, "generated_at": timezone.now().isoformat()}, timeout=600)
    return f"Saved {len(emails)} users to cache"


@shared_task
def delete_unactive_users():
    """Crontab example: ежедневно очищаем неактивных пользователей."""
    from users.models import CustomUser

    deleted = CustomUser.objects.filter(is_active=False).delete()
    return f"Deleted: {deleted}"


@shared_task
def send_daily_report_email():
    """SMTP example: отправляем бизнес-отчёт по email."""
    from users.models import CustomUser

    total_users = CustomUser.objects.count()
    subject = "Daily user report"
    message = f"На сегодня в системе {total_users} пользователей."
    send_mail(subject, message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], fail_silently=False)
    return message
