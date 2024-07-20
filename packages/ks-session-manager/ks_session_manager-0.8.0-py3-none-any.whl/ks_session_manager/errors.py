class ConverterError(Exception):
    pass


class SigningInDisabledError(RuntimeError):
    def __init__(self, code_type: str):
        super().__init__("Session is not signed in")
        self.code_type = code_type


class ConverterSessionUnauthorized(ConverterError):
    def __init__(self, message: str, original_exception: Exception):
        super().__init__(message)
        self.original_exception = original_exception


class ConverterSessionUnauthorizedYetError(ConverterError):
    pass


class ConverterMissingSessionData(ConverterError):
    pass


class ConverterUnableToCollectUserInfo(ConverterError):
    pass
