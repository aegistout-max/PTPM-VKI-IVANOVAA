from registration import mask, validate


def test_ok():
    assert validate("ivan_2024", "Parol12!", "Parol12!") == (True, "")
    assert validate("name@mail.ru", "Parol12!", "Parol12!") == (True, "")
    assert validate("+7-999-123-4567", "Parol12!", "Parol12!") == (True, "")


def test_bad_login():
    assert validate("admin", "Parol12!", "Parol12!")[0] is False
    assert validate("ab", "Parol12!", "Parol12!")[0] is False


def test_bad_password():
    assert validate("ivan_2024", "parol", "parol")[0] is False


def test_mismatch():
    assert validate("ivan_2024", "Parol12!", "Parol13!")[0] is False


def test_mask():
    assert mask("Parol12!") == "********"
