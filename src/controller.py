class Controller:
    def __init__(self, user_input, database, validator, external):
        self.user_input = user_input
        self.database = database
        self.validator = validator
        self.external = external

    def execute(self):
        login, password, confirm = self.user_input.get_data()
        stored = self.database.get(login, password, confirm)
        if stored is None:
            result, message = self.validator.validate(login, password, confirm)
            self.database.add(login, password, confirm, result, message)
        else:
            result, message = stored

        if result:
            text = "регистрация успешна"
        else:
            text = message
        self.external.send(text)
        return result, message
