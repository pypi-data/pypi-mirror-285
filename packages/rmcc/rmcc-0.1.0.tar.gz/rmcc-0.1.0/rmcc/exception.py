class RmccError(Exception):
    def __init__(self, arg=""):
        self.arg = arg


class UnimplementedError(RmccError):
    def __str__(self):
        return f"{self.arg} mesh code dimension is unimplemented."


class ParseError(RmccError):
    def __str__(self):
        return f"{self.arg} could not be parsed."


class InvalidElementError(RmccError):
    def __str__(self):
        return f"{self.arg} is invalid element."
