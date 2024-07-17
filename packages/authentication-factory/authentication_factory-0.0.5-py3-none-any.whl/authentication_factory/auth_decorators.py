from abc import ABC, abstractmethod


class AuthDecorators(ABC):
    @abstractmethod
    def login_handler(self, config: dict):
        pass

    @abstractmethod
    def logout_handler(self):
        pass

    @abstractmethod
    def callback_handler(self):
        pass
