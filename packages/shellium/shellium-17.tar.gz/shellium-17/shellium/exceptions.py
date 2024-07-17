class ShelliumException(Exception):
    def __init__(self, message):
        super().__init__(message)


class UserDataDirExistsError(ShelliumException):
    def __init__(self, message):
        super().__init__(message)


class UserDataDirBuildError(ShelliumException):
    def __init__(self, message):
        super().__init__(message)


class ChromeAlreadyRunningError(ShelliumException):
    def __init__(self, message):
        super().__init__(message)


class ChromeVersionError(ShelliumException):
    def __init__(self, message):
        super().__init__(message)
