from apps.client.application.dto.client_inputs import DeleteClientInput
from apps.client.application.ports.client_repository import ClientRepository


class DeleteClient:
    def __init__(self, repo: ClientRepository):
        self.repo = repo

    def execute(self, inp: DeleteClientInput) -> None:
        self.repo.delete(inp.client_id)
