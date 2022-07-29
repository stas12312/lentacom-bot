class LentaBaseException(Exception):

    def __init__(self, message: str, error_code: int) -> None:
        self.message = message
        self.error_code = error_code

    def __str__(self):
        return f"{self.error_code} - {self.message}"


class LentaRequestError(LentaBaseException):
    def __init__(
            self,
            message: str,
            error_code: int,
            url: str,
    ):
        super().__init__(message, error_code)
        self.url = url

    def __str__(self):
        return f'[{self.url}] - {self.error_code}: {self.message}'
