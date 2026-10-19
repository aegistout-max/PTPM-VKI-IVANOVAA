import io
import os
import runpy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from controller import Controller
from database import RegistrationDatabase
from notifier import EmailNotifier, ExternalService
from user_input import ConsoleUserInput, UserInput
from validator import RegistrationValidator

ROOT = Path(__file__).resolve().parents[1]
VALID = ("ivan_2024", "Parol12!", "Parol12!")


class CountingValidator(RegistrationValidator):
    def __init__(self):
        self.calls = 0

    def validate(self, login, password, confirm):
        self.calls += 1
        return super().validate(login, password, confirm)


def build(data, database=None, validator=None, external=None):
    user = Mock(spec=UserInput)
    user.get_data.return_value = data
    database = database or RegistrationDatabase()
    validator = validator or RegistrationValidator()
    external = external or Mock(spec=ExternalService)
    controller = Controller(user, database, validator, external)
    return controller, database, validator, external


class IntegrationTests(unittest.TestCase):
    def test_new_registration_is_saved_and_sent(self):
        controller, database, validator, external = build(VALID)
        self.assertIsNone(database.get(*VALID))

        result = controller.execute()

        self.assertEqual(result, (True, ""))
        self.assertEqual(database.get(*VALID), (True, ""))
        external.send.assert_called_once_with("регистрация успешна")
        self.assertIsInstance(validator, RegistrationValidator)
        database.close()

    def test_known_registration_comes_from_database(self):
        database = RegistrationDatabase()
        database.add("ab", "Parol12!", "Parol12!", False, "из базы")
        validator = Mock(spec=RegistrationValidator)
        controller, database, validator, external = build(
            ("ab", "Parol12!", "Parol12!"),
            database=database,
            validator=validator,
        )

        result = controller.execute()

        self.assertEqual(result, (False, "из базы"))
        validator.validate.assert_not_called()
        external.send.assert_called_once_with("из базы")
        database.close()

    def test_second_request_does_not_validate_again(self):
        validator = CountingValidator()
        database = RegistrationDatabase()
        controller, database, validator, external = build(
            VALID,
            database=database,
            validator=validator,
        )

        first = controller.execute()
        second = controller.execute()

        self.assertEqual(first, (True, ""))
        self.assertEqual(second, (True, ""))
        self.assertEqual(validator.calls, 1)
        self.assertEqual(database.get(*VALID), (True, ""))
        self.assertEqual(external.send.call_count, 2)
        database.close()

    def test_pipeline_saves_and_sends_every_outcome(self):
        cases = [
            ("", "Parol12!", "Parol12!", False, "логин не может быть пустым"),
            ("admin", "Parol12!", "Parol12!", False, "Такой логин использовать нельзя"),
            ("+7-999-123-45", "Parol12!", "Parol12!", False, "телефон должен быть в формате +7-999-123-4567"),
            ("+7-999-123-4567", "Parol12!", "Parol12!", True, ""),
            ("name@mail", "Parol12!", "Parol12!", False, "email должен быть в формате name@mail.ru"),
            ("name@mail.ru", "Parol12!", "Parol12!", True, ""),
            ("ab", "Parol12!", "Parol12!", False, "логин короче 5 символов"),
            ("иван_2024", "Parol12!", "Parol12!", False, "В логине можно только латиницу, цифры и _"),
            ("ivan_2024", "", "", False, "пароль не может быть пустым"),
            ("ivan_2024", "Par12!", "Par12!", False, "Пароль короче 7 символов"),
            ("ivan_2024", "Пароль1!", "Пароль1!", False, "только латиница цифры и спецсимволы"),
            ("ivan_2024", "parol12!", "parol12!", False, "нет заглавной буквы"),
            ("ivan_2024", "PAROL12!", "PAROL12!", False, "нет строчной буквы"),
            ("ivan_2024", "Parol!!", "Parol!!", False, "нет цифры"),
            ("ivan_2024", "Parol123", "Parol123", False, "нет спецсимвола"),
            ("ivan_2024", "Parol12!", "", False, "подтверждение пароля не может быть пустым"),
            ("ivan_2024", "Parol12!", "Parol13!", False, "пароли не совпадают"),
            VALID + (True, ""),
        ]
        for login, password, confirm, expected, message in cases:
            with self.subTest(login=login, password=password, confirm=confirm):
                controller, database, validator, external = build((login, password, confirm))
                result = controller.execute()
                sent = "регистрация успешна" if expected else message
                self.assertEqual(result, (expected, message))
                self.assertEqual(database.get(login, password, confirm), (expected, message))
                external.send.assert_called_once_with(sent)
                database.close()


class IsolationTests(unittest.TestCase):
    def test_input_and_email_are_replaced_by_stubs(self):
        user = Mock(spec=UserInput)
        user.get_data.return_value = VALID
        external = Mock(spec=ExternalService)
        database = RegistrationDatabase()
        controller = Controller(
            user,
            database,
            RegistrationValidator(),
            external,
        )

        with patch("builtins.input", side_effect=AssertionError("реальный ввод")):
            result = controller.execute()

        self.assertEqual(result, (True, ""))
        user.get_data.assert_called_once_with()
        external.send.assert_called_once_with("регистрация успешна")
        database.close()

    def test_console_input_reads_three_fields(self):
        answers = ["ivan_2024", "Parol12!", "Parol12!"]
        with patch("builtins.input", side_effect=answers) as mocked_input:
            data = ConsoleUserInput().get_data()

        self.assertEqual(data, VALID)
        self.assertEqual(mocked_input.call_count, 3)

    def test_email_notifier_simulates_send(self):
        notifier = EmailNotifier()
        notifier.send("регистрация успешна")
        self.assertEqual(notifier.sent, ["регистрация успешна"])

    def test_interfaces_declare_input_and_send(self):
        class InputProbe(UserInput):
            def get_data(self):
                return super().get_data()

        class SendProbe(ExternalService):
            def send(self, message):
                return super().send(message)

        self.assertIsNone(InputProbe().get_data())
        self.assertIsNone(SendProbe().send("проверка"))

    def test_database_add_get_delete(self):
        database = RegistrationDatabase()
        self.assertIsNone(database.get(*VALID))
        database.add(*VALID, True, "")
        self.assertEqual(database.get(*VALID), (True, ""))
        database.delete(*VALID)
        self.assertIsNone(database.get(*VALID))
        database.close()

    def test_script_entrypoint(self):
        with tempfile.TemporaryDirectory() as folder:
            previous = os.getcwd()
            os.chdir(folder)
            try:
                with patch("builtins.input", side_effect=list(VALID)):
                    with patch("sys.stdout", new_callable=io.StringIO) as output:
                        runpy.run_path(str(ROOT / "main.py"), run_name="__main__")
            finally:
                os.chdir(previous)

        self.assertIn("True", output.getvalue())


if __name__ == "__main__":
    unittest.main()
