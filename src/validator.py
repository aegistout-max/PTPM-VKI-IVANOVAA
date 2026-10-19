import re

BLACKLIST = ["admin", "root", "guest", "user", "test", "support", "null", "anonymous"]

LOWER = "abcdefghijklmnopqrstuvwxyz"
UPPER = LOWER.upper()
DIGITS = "0123456789"
SPECIALS = "!@#$%^&*()-_=+.,:;?"


class RegistrationValidator:
    def validate(self, login, password, confirm):
        if login == "":
            return False, "логин не может быть пустым"

        if login.lower() in BLACKLIST:
            return False, "Такой логин использовать нельзя"

        if login.startswith("+"):
            if not re.fullmatch(r"\+\d-\d{3}-\d{3}-\d{4}", login):
                return False, "телефон должен быть в формате +7-999-123-4567"
        elif "@" in login:
            if not re.fullmatch(r"[a-zA-Z0-9._-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}", login):
                return False, "email должен быть в формате name@mail.ru"
        else:
            if len(login) < 5:
                return False, "логин короче 5 символов"
            for char in login:
                if char not in LOWER + UPPER + DIGITS + "_":
                    return False, "В логине можно только латиницу, цифры и _"

        if password == "":
            return False, "пароль не может быть пустым"

        if len(password) < 7:
            return False, "Пароль короче 7 символов"

        for char in password:
            if char not in LOWER + UPPER + DIGITS + SPECIALS:
                return False, "только латиница цифры и спецсимволы"

        if not any(char in UPPER for char in password):
            return False, "нет заглавной буквы"
        if not any(char in LOWER for char in password):
            return False, "нет строчной буквы"
        if not any(char in DIGITS for char in password):
            return False, "нет цифры"
        if not any(char in SPECIALS for char in password):
            return False, "нет спецсимвола"

        if confirm == "":
            return False, "подтверждение пароля не может быть пустым"

        if password != confirm:
            return False, "пароли не совпадают"

        return True, ""
