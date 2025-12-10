import logging
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """
    Send an email using SMTP.

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        text_content: Plain text content (optional)

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if not settings.ENABLE_EMAIL:
        logger.info(
            f"Email sending is disabled. Would have sent email to {to_email} with subject: {subject}")
        return True

    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP settings not configured. Cannot send email.")
        return False

    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["From"] = settings.SMTP_USER
        message["To"] = to_email
        message["Subject"] = subject

        # Add text and HTML parts
        if text_content:
            part1 = MIMEText(text_content, "plain")
            message.attach(part1)

        part2 = MIMEText(html_content, "html")
        message.attach(part2)

        # Send email
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True
        )

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


async def send_verification_email(email: str, verification_token: str) -> bool:
    """
    Send email verification link to user.

    Args:
        email: User's email address
        verification_token: Verification token

    Returns:
        bool: True if email was sent successfully
    """
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"

    subject = "Verify Your Email - Data Analytics SaaS"

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4F46E5;">Welcome to Data Analytics SaaS!</h2>
                <p>Thank you for signing up. Please verify your email address by clicking the button below:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}"
                       style="background-color: #4F46E5; color: white; padding: 12px 30px;
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Verify Email
                    </a>
                </div>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #4F46E5;">{verification_url}</p>
                <p style="margin-top: 30px; font-size: 12px; color: #666;">
                    If you didn't create an account, you can safely ignore this email.
                </p>
            </div>
        </body>
    </html>
    """

    text_content = f"""
    Welcome to Data Analytics SaaS!

    Thank you for signing up. Please verify your email address by visiting:
    {verification_url}

    If you didn't create an account, you can safely ignore this email.
    """

    return await send_email(email, subject, html_content, text_content)


async def send_password_reset_email(email: str, reset_token: str) -> bool:
    """
    Send password reset link to user.

    Args:
        email: User's email address
        reset_token: Password reset token

    Returns:
        bool: True if email was sent successfully
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"

    subject = "Reset Your Password - Data Analytics SaaS"

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4F46E5;">Password Reset Request</h2>
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}"
                       style="background-color: #4F46E5; color: white; padding: 12px 30px;
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #4F46E5;">{reset_url}</p>
                <p style="margin-top: 30px; font-size: 12px; color: #666;">
                    This link will expire in 1 hour. If you didn't request a password reset,
                    you can safely ignore this email.
                </p>
            </div>
        </body>
    </html>
    """

    text_content = f"""
    Password Reset Request

    We received a request to reset your password. Visit the following link to create a new password:
    {reset_url}

    This link will expire in 1 hour. If you didn't request a password reset, you can safely ignore this email.
    """

    return await send_email(email, subject, html_content, text_content)
