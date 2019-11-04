class Parser:
    filename = None

    def __init__(self, filename):
        self.filename = filename

    def parse(self) -> dict:
        d = {}
        n = 1
        with open(self.filename, "r") as handle:
            for line in handle:
                try:
                    r = Parser.deserialize_property(line)
                    if r is not None:
                        d[r[0]] = r[1]
                    n += 1
                except SyntaxError as e:
                    raise SyntaxError("Error in line " + str(n)) from e

        return d

    def write(self, payload: dict):
        with open(self.filename, "w") as handle:
            for name, value in payload.items():
                handle.write(Parser.serialize_property(name, value) + "\n")

    @staticmethod
    def serialize_property(name: str, value: str):
        if name.find("=") > -1:
            raise SyntaxError("Equals sign not allowed as property name")
        return "%s=%s" % (name, value)

    @staticmethod
    def deserialize_property(line: str):
        if line.strip().startswith("#") or len(line.strip()) == 0:
            return None

        comment = line.find("#")
        if comment == -1:
            comment = len(line)

        prop = line[:comment]
        separator = prop.find("=")
        if separator == -1:
            raise SyntaxError("Missing equals sign")

        name = prop[0:separator].strip()
        value = prop[separator + 1:].replace("\r\n", "").replace("\n", "")

        return [name, value]
