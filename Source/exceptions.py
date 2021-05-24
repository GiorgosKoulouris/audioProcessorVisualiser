class FilePathException(Exception):
    """Custom exception raised when an undesired file path appears"""

    def __init__(self, msg='Invalid input', error=""):
        self.message = msg
        self.error = error

    def __str__(self):
        r = f'UserInputExeption: {self.message}\n  {self.error}\n'
        return r


class UserInputExeption(Exception):
    """Custom exception raised when user inputs values
    that are not allowed or are meaningless"""

    def __init__(self, msg='Invalid input', error=""):
        self.message = msg
        self.error = error

    def __str__(self):
        r = f'UserInputExeption: {self.message}\n  {self.error}\n'
        return r


class ScriptReturnCodeException(Exception):
    """Custom exception raised when scripts return failure values"""

    def __init__(self, msg='Invalid input', error=""):
        self.message = msg
        self.error = error

    def __str__(self):
        r = f'UserInputExeption: {self.message}\n  {self.error}\n'
        return r
