class FilePathException(Exception):
    """Custom exception raised when an undesired file path appears"""

    def __init__(self, message, error=None):
        self.message = message
        self.error = error

    def __str__(self):
        return (f'FilePathException: {self.message}')


class UserInputExeption(Exception):
    """Custom exception raised when user inputs values that are not allowed or are meaningless"""

    def __init__(self, message, error=None):
        self.message = message
        self.error = error

    def __str__(self):
        return (f'UserInputExeption: {self.message}')


class ScriptReturnCodeException(Exception):
    """Custom exception raised when scripts return failure values"""

    def __init__(self, message, error=None):
        self.message = message
        self.error = error

    def __str__(self):
        return (f'ScriptReturnCodeException: {self.message}')
