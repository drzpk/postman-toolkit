class Log:
    debug = False

    @staticmethod
    def i(msg: str):
        print("[i] %s" % msg)

    @staticmethod
    def d(msg: str):
        if Log.debug:
            print("[d] %s" % msg)
