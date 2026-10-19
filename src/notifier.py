from abc import ABC, abstractmethod


class ExternalService(ABC):
    @abstractmethod
    def send(self, message):
        """Передаёт строку результата стороннему процессу."""
        return None


class EmailNotifier(ExternalService):
    def __init__(self):
        self.sent = []

    def send(self, message):
        self.sent.append(message)
