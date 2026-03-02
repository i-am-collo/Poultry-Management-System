import unittest

from pydantic import ValidationError

from app.schemas.auth import RegisterRequest, ResetPasswordRequest


class AuthSchemaTests(unittest.TestCase):
    def test_register_allows_supported_roles(self) -> None:
        payload = RegisterRequest(
            name="Farmer Example",
            email="farmer@example.com",
            phone="+15550000010",
            role="farmer",
            password="StrongPass123!",
        )
        self.assertEqual(payload.role, "farmer")

    def test_register_rejects_admin_role(self) -> None:
        with self.assertRaises(ValidationError):
            RegisterRequest(
                name="Admin Example",
                email="admin@example.com",
                phone="+15550000011",
                role="admin",
                password="StrongPass123!",
            )

    def test_register_rejects_password_over_72_utf8_bytes(self) -> None:
        too_long_utf8_password = "😀" * 19  # 76 bytes in UTF-8
        with self.assertRaises(ValidationError):
            RegisterRequest(
                name="Emoji User",
                email="emoji@example.com",
                phone="+15550000012",
                role="buyer",
                password=too_long_utf8_password,
            )

    def test_reset_password_rejects_password_over_72_utf8_bytes(self) -> None:
        too_long_utf8_password = "😀" * 19
        with self.assertRaises(ValidationError):
            ResetPasswordRequest(
                token="dummy-token",
                new_password=too_long_utf8_password,
            )
