import asyncio
from app.services.email_services import send_email, send_password_reset_email

async def test_basic_email():
    """Test basic email sending"""
    result = await send_email(
        email="iamcollolimo@gmail.com",
        subject="Test Email from Poultry Management System",
        body="<h1>Hello!</h1><p>This is a test email.</p>",
        html=True
    )
    print("Basic Email Test:", result)

async def test_password_reset():
    """Test password reset email"""
    result = await send_password_reset_email(
        email="iamcollolimo@gmail.com",
        reset_token="test-token-12345"
    )
    print("Password Reset Email Test:", result)

async def main():
    print("Starting email tests...\n")
    await test_basic_email()
    await test_password_reset()

if __name__ == "__main__":
    asyncio.run(main())