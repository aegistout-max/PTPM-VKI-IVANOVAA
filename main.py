import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from controller import Controller
from database import RegistrationDatabase
from notifier import EmailNotifier
from user_input import ConsoleUserInput
from validator import RegistrationValidator


def main(db_path="registrations.db"):
    database = RegistrationDatabase(db_path)
    controller = Controller(
        ConsoleUserInput(),
        database,
        RegistrationValidator(),
        EmailNotifier(),
    )
    try:
        result, message = controller.execute()
        print(result)
        print(message)
    finally:
        database.close()


if __name__ == "__main__":
    main()
