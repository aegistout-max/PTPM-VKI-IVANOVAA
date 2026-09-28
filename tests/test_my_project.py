import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from my_project import mask, validate


class TestRegistration(unittest.TestCase):
    def test_accepts_valid_login_email_and_phone(self):
        self.assertEqual(validate("ivan_2024", "Parol12!", "Parol12!"), (True, ""))
        self.assertEqual(validate("login", "Abc12!@", "Abc12!@"), (True, ""))
        self.assertEqual(validate("name@mail.ru", "Parol12!", "Parol12!"), (True, ""))
        self.assertEqual(validate("+7-999-123-4567", "Parol12!", "Parol12!"), (True, ""))

    def test_rejects_empty_login(self):
        self.assertEqual(validate("", "Parol12!", "Parol12!"), (False, "логин не может быть пустым"))

    def test_rejects_blacklisted_login_in_any_case(self):
        self.assertEqual(validate("admin", "Parol12!", "Parol12!"), (False, "Такой логин использовать нельзя"))
        self.assertEqual(validate("AdMiN", "Parol12!", "Parol12!"), (False, "Такой логин использовать нельзя"))
        self.assertEqual(validate("root", "Parol12!", "Parol12!"), (False, "Такой логин использовать нельзя"))

    def test_rejects_short_or_forbidden_ordinary_login(self):
        self.assertEqual(validate("ab", "Parol12!", "Parol12!"), (False, "логин короче 5 символов"))
        self.assertEqual(validate("иван_2024", "Parol12!", "Parol12!"), (False, "В логине можно только латиницу, цифры и _"))
        self.assertEqual(validate("ivan-2024", "Parol12!", "Parol12!"), (False, "В логине можно только латиницу, цифры и _"))

    def test_rejects_phone_and_email_with_wrong_mask(self):
        self.assertEqual(validate("+7-999-123-45", "Parol12!", "Parol12!"), (False, "телефон должен быть в формате +7-999-123-4567"))
        self.assertEqual(validate("name@mail", "Parol12!", "Parol12!"), (False, "email должен быть в формате name@mail.ru"))

    def test_rejects_empty_or_short_password(self):
        self.assertEqual(validate("ivan_2024", "", ""), (False, "пароль не может быть пустым"))
        self.assertEqual(validate("ivan_2024", "Par12!", "Par12!"), (False, "Пароль короче 7 символов"))

    def test_rejects_password_without_required_symbol_classes(self):
        self.assertEqual(validate("ivan_2024", "parol12!", "parol12!"), (False, "нет заглавной буквы"))
        self.assertEqual(validate("ivan_2024", "PAROL12!", "PAROL12!"), (False, "нет строчной буквы"))
        self.assertEqual(validate("ivan_2024", "Parol!!", "Parol!!"), (False, "нет цифры"))
        self.assertEqual(validate("ivan_2024", "Parol123", "Parol123"), (False, "нет спецсимвола"))

    def test_rejects_password_with_forbidden_characters(self):
        self.assertEqual(validate("ivan_2024", "Пароль1!", "Пароль1!"), (False, "только латиница цифры и спецсимволы"))

    def test_rejects_empty_or_mismatched_confirmation(self):
        self.assertEqual(validate("ivan_2024", "Parol12!", ""), (False, "подтверждение пароля не может быть пустым"))
        self.assertEqual(validate("ivan_2024", "Parol12!", "Parol13!"), (False, "пароли не совпадают"))

    def test_mask_hides_password_and_keeps_length(self):
        self.assertEqual(mask("Parol12!"), "********")
        self.assertNotIn("Parol", mask("Parol12!"))
        self.assertEqual(len(mask("Abc12!@")), 7)


if __name__ == "__main__":
    unittest.main()
