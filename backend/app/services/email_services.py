import os
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import EmailStr

# Load environment variables from .env file
load_dotenv()

# Email configuration using environment variables
conf = ConnectionConfig(
    MAIL_SERVER=os.getenv("EMAIL_HOST"),
    MAIL_PORT=int(os.getenv("EMAIL_PORT", "587")),
    MAIL_STARTTLS=os.getenv("EMAIL_USE_TLS", "True") == "True",
    MAIL_USERNAME=os.getenv("EMAIL_HOST_USER"),
    MAIL_PASSWORD=os.getenv("EMAIL_HOST_PASSWORD"),
    MAIL_FROM=os.getenv("DEFAULT_FROM_EMAIL"),
    MAIL_SSL_TLS=False,
)

# Initialize FastMail instance
fm = FastMail(conf)

async def send_email(email: EmailStr, subject: str, body: str, html: bool = False):
    """
    Send email via SMTP
    
    Args:
        email: Recipient email address
        subject: Email subject
        body: Email body (HTML or plain text)
        html: If True, body is treated as HTML
    """
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=body,
            subtype="html" if html else "plain",
        )
        
        await fm.send_message(message)
        return {"status": "success", "message": f"Email sent to {email}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def send_welcome_email(email: EmailStr, name: str, base_url: str = "http://localhost:3000"):
    """Send welcome email to new registered users"""
    subject = "Welcome to Poultry Management System"
    body = f"""
    <h2>Welcome to Poultry Management System!</h2>
    <p>Hi {name},</p>
    <p>Thank you for registering with us. Your account has been successfully created.</p>
    <p>You can now log in and start managing your poultry operations.</p>
    <p><a href="{base_url}/login.html">Log In Here</a></p>
    <br>
    <p>If you have any questions, feel free to contact our support team.</p>
    <p>Best regards,<br>Poultry Management System Team</p>
    """
    return await send_email(email, subject, body, html=True)

async def send_password_reset_email(email: EmailStr, reset_token: str, base_url: str = "http://localhost:3000"):
    """Send password reset email"""
    reset_link = f"{base_url}/auth/forgot_password/reset_password.html?token={reset_token}"
    subject = "Poultry Management System - Password Reset"
    body = f"""
    <h2>Password Reset Request</h2>
    <p>We received a request to reset your password. Click the link below to proceed:</p>
    <a href="{reset_link}">Reset Password</a>
    <p>This link expires in 60 minutes.</p>
    <p>If you didn't request a password reset, please ignore this email.</p>
    <br>
    <p>Best regards,<br>Poultry Management System Team</p>
    """
    return await send_email(email, subject, body, html=True)

async def send_order_notification(email: EmailStr, order_id: str, status: str):
    """Send order status notification"""
    subject = f"Order #{order_id} - Status Update"
    body = f"""
    <h2>Order Notification</h2>
    <p>Your order <strong>#{order_id}</strong> status has been updated to: <strong>{status}</strong></p>
    """
    return await send_email(email, subject, body, html=True)