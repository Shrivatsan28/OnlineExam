from django.core.mail import send_mail
from django.conf import settings


def send_student_email(subject: str, message: str, recipient_email: str) -> None:
    """Send a plain-text email to a student, silently swallowing send errors."""
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [recipient_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send '{subject}' to {recipient_email}: {e}")
