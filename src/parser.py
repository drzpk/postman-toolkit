class Parser:
    handle = None

    def __init__(self, file):
        self.handle = open(file, "r")

    def __del__(self):
        self.handle.close()

    def parse(self):
        d = {}
        n = 1
        for line in self.handle:
            try:
                r = Parser.deserialize_property(line)
                if r is not None:
                    d[r[0]] = r[1]
                n += 1
            except SyntaxError as e:
                raise SyntaxError("Error in line " + str(n), e)

        return d

    @staticmethod
    def serialize_property(name: str, value: str):
        if name.find("=") > -1:
            raise SyntaxError("Equals sign not allowed as property name")
        return "%s=%s" % (name, value)

    @staticmethod
    def deserialize_property(line: str):
        if line.strip().startswith("#"):
            return None

        comment = line.find("#")
        if comment == -1:
            comment = len(line)

        prop = line[:comment]
        separator = prop.find("=")
        if separator == -1:
            raise SyntaxError("Missing equals sign")

        name = prop[0:separator].strip()
        value = prop[separator + 1:]

        return [name, value]
