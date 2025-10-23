# apps/client/application/errors.py
class RepositoryError(Exception):
    def __init__(self, message: str, original_error: Exception | None = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)


class NotFoundError(Exception): ...


class ConflictError(Exception): ...
