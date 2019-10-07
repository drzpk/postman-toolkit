class Log:

    @staticmethod
    def i(msg: str):
        print("[i] %s" % msg)

    @staticmethod
    def d(msg: str):
        # TODO: debug mode
        print("[d] %s" % msg)
