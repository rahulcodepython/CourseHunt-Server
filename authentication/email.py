from typing import Dict, Optional
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from smtplib import SMTPException
from logging import getLogger

# Initialize logger for email operations
logger = getLogger(__name__)

# Common template context keys
TEMPLATE_CONTEXT = {
    "company_name": settings.COMPANY_NAME,
    "host_email": settings.EMAIL_HOST_USER,
}


def send_email(
    subject: str,
    template_name: str,
    context: Dict[str, str],
    to_email: str,
) -> bool:
    """
    Generic email sending function with error handling.

    Args:
        subject: Email subject line
        template_name: HTML template file name
        context: Template context dictionary
        to_email: Recipient email address

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        html_body = render_to_string(
            template_name, {**TEMPLATE_CONTEXT, **context})
        msg = EmailMultiAlternatives(
            subject=subject,
            from_email=settings.EMAIL_HOST_USER,
            to=[to_email]
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        return True
    except SMTPException as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


def ActivationEmail(uid: str, token: str, email: str, username: str) -> Optional[bool]:
    """Send email verification link to user."""
    if not settings.SEND_ACTIVATION_EMAIL:
        return None

    return send_email(
        subject="Verify Your Email Address - Action Required",
        template_name="activation.html",
        context={
            "username": username,
            "uid": uid,
            "token": token,
        },
        to_email=email,
    )


def ResetPasswordConfirmation(uid: str, token: str, email: str, username: str) -> Optional[bool]:
    """Send password reset confirmation email."""
    if not settings.SEND_RESET_PASSWORD_CONFIRMATION_EMAIL:
        return None

    return send_email(
        subject="Reset Password Confirmation - Action Required",
        template_name="reset_password_confirmation.html",
        context={
            "username": username,
            "uid": uid,
            "token": token,
        },
        to_email=email,
    )


def ResetEmailConfirmation(uid: str, token: str, email: str, username: str) -> Optional[bool]:
    """Send email change confirmation email."""
    if not settings.SEND_RESET_EMAIL_CONFIRMATION_EMAIL:
        return None

    return send_email(
        subject="Reset Email Confirmation - Action Required",
        template_name="reset_email_confirmation.html",
        context={
            "username": username,
            "uid": uid,
            "token": token,
        },
        to_email=email,
    )


def LoginConfirmation(uid: str, token: str, email: str, username: str) -> Optional[bool]:
    """Send login confirmation email."""
    if not settings.SEND_LOGIN_CONFIRMATION_EMAIL:
        return None

    return send_email(
        subject="Login Confirmation - Action Required",
        template_name="login_confirmation.html",
        context={
            "username": username,
            "uid": uid,
            "token": token,
        },
        to_email=email,
    )
