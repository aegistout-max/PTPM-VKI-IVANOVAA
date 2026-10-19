from abc import ABC, abstractmethod


class UserInput(ABC):
    @abstractmethod
    def get_data(self):
        """Возвращает логин, пароль и подтверждение пароля."""
        return None


class ConsoleUserInput(UserInput):
    def get_data(self):
        login = input("Логин: ")
        password = input("Пароль: ")
        confirm = input("Повтор пароля: ")
        return login, password, confirm
