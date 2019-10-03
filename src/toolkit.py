from .config import Configuration


VERSION = "1.0"


class PostmanToolkit:

    @staticmethod
    def start():
        Configuration.initialize()
