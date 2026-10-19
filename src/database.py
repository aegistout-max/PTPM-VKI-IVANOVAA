import sqlite3


class RegistrationDatabase:
    def __init__(self, db_path=":memory:"):
        self.connection = sqlite3.connect(db_path)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                login TEXT NOT NULL,
                password TEXT NOT NULL,
                confirm TEXT NOT NULL,
                auth_result INTEGER NOT NULL,
                error_message TEXT NOT NULL,
                PRIMARY KEY (login, password, confirm)
            )
            """
        )
        self.connection.commit()

    def close(self):
        self.connection.close()

    def add(self, login, password, confirm, result, error_message):
        self.connection.execute(
            """
            INSERT INTO registrations
                (login, password, confirm, auth_result, error_message)
            VALUES (?, ?, ?, ?, ?)
            """,
            (login, password, confirm, int(bool(result)), error_message),
        )
        self.connection.commit()

    def get(self, login, password, confirm):
        row = self.connection.execute(
            """
            SELECT auth_result, error_message
            FROM registrations
            WHERE login = ? AND password = ? AND confirm = ?
            """,
            (login, password, confirm),
        ).fetchone()
        if row is None:
            return None
        return bool(row[0]), row[1]

    def delete(self, login, password, confirm):
        self.connection.execute(
            """
            DELETE FROM registrations
            WHERE login = ? AND password = ? AND confirm = ?
            """,
            (login, password, confirm),
        )
        self.connection.commit()
