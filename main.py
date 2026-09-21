import logging
import sys

from registration import mask, validate


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | [%(levelname)-7s] | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/file_txt.log", encoding="utf-8"),
        ],
    )
    logging.info("Логгер успешно сконфигурирован")
    logging.info("Приложение запущено")

    login = input("Логин: ")
    password = input("Пароль: ")
    confirm = input("Повтор пароля: ")
    logging.debug(
        "Запрос: логин=%s, пароль=%s, повтор=%s",
        login,
        mask(password),
        mask(confirm),
    )

    try:
        result, message = validate(login, password, confirm)
    except Exception:
        logging.exception("Ошибка при проверке данных")
        result, message = False, "Внутренняя ошибка программы"

    if result:
        logging.info(
            "Успешный запрос: логин=%s, пароль=%s, повтор=%s, результат=%s",
            login,
            mask(password),
            mask(confirm),
            result,
        )
    else:
        logging.warning(
            "Неуспешный запрос: логин=%s, пароль=%s, повтор=%s, ошибка=%s",
            login,
            mask(password),
            mask(confirm),
            message,
        )

    print(result)
    print(message)


if __name__ == "__main__":
    main()
