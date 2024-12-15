from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def ActivationEmail(uid, token, email, username):
    if settings.SEND_ACTIVATION_EMAIL:
        subject = "Verify Your Email Address - Action Required"
        html_body = render_to_string(
            "activation.html",
            {
                "username": username,
                "company_name": settings.COMPANY_NAME,
                "host_email": settings.EMAIL_HOST_USER,
                "uid": uid,
                "token": token,
            },
        )

        msg = EmailMultiAlternatives(
            subject=subject, from_email=settings.EMAIL_HOST_USER, to=[email]
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()


def ResetPasswordConfirmation(uid, token, email, username):
    if settings.SEND_RESET_PASSWORD_CONFIRMATION_EMAIL:
        subject = "Reset Password Confirmation - Action Required"
        html_body = render_to_string(
            "reset_password_confirmation.html",
            {
                "username": username,
                "company_name": settings.COMPANY_NAME,
                "host_email": settings.EMAIL_HOST_USER,
                "uid": uid,
                "token": token,
            },
        )

        msg = EmailMultiAlternatives(
            subject=subject, from_email=settings.EMAIL_HOST_USER, to=[email]
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()


def ResetEmailConfirmation(uid, token, email, username):
    if settings.SEND_RESET_EMAIL_CONFIRMATION_EMAIL:
        subject = "Reset Email Confirmation - Action Required"
        html_body = render_to_string(
            "reset_email_confirmation.html",
            {
                "username": username,
                "company_name": settings.COMPANY_NAME,
                "host_email": settings.EMAIL_HOST_USER,
                "uid": uid,
                "token": token,
            },
        )

        msg = EmailMultiAlternatives(
            subject=subject, from_email=settings.EMAIL_HOST_USER, to=[email]
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()


def LoginConfirmation(uid, token, email, username):
    if settings.SEND_LOGIN_CONFIRMATION_EMAIL:
        subject = "Login Confirmation - Action Required"
        html_body = render_to_string(
            "login_confirmation.html",
            {
                "username": username,
                "company_name": settings.COMPANY_NAME,
                "host_email": settings.EMAIL_HOST_USER,
                "uid": uid,
                "token": token,
            },
        )

        msg = EmailMultiAlternatives(
            subject=subject, from_email=settings.EMAIL_HOST_USER, to=[email]
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
