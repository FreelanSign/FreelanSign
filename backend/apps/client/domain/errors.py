# apps/client/domain/errors.py
class ClientDomainError(Exception):
    def __init__(self, message: str, code: str = "CLIENT_DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class ClientPolicyError(ClientDomainError):
    def __init__(self, message: str, code: str = "CLIENT_POLICY_ERROR"):
        super().__init__(message, code="CLIENT_POLICY_ERROR")


class ClientNotFoundError(ClientDomainError):
    def __init__(self, client_id: str, code: str = "CLIENT_NOT_FOUND"):
        super().__init__(f"Client not found: {client_id}", code="CLIENT_NOT_FOUND")


class ClientAlreadyExistsError(ClientPolicyError):
    def __init__(self, name: str, code: str = "CLIENT_ALREADY_EXISTS"):
        super().__init__(f"Client already exists: {name}", code="CLIENT_ALREADY_EXISTS")


class ClientInvalidNameError(ClientPolicyError):
    def __init__(self, name: str, code: str = "CLIENT_INVALID_NAME"):
        super().__init__(f"Client invalid name: {name}", code="CLIENT_INVALID_NAME")
