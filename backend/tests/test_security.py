import unittest

from app.core.security import hash_password, verify_password


class SecurityTests(unittest.TestCase):
    def test_hash_and_verify_password(self) -> None:
        password = "StrongPass123!"
        hashed = hash_password(password)

        self.assertNotEqual(password, hashed)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("WrongPass123!", hashed))

    def test_hash_password_rejects_over_72_utf8_bytes(self) -> None:
        too_long_password = "a" * 73
        with self.assertRaises(ValueError):
            hash_password(too_long_password)

    def test_verify_password_returns_false_for_over_72_utf8_bytes(self) -> None:
        hashed = hash_password("ValidPass123!")
        too_long_password = "a" * 73
        self.assertFalse(verify_password(too_long_password, hashed))
