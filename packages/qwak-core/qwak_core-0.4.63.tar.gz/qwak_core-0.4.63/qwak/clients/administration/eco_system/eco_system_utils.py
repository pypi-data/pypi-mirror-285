from qwak.clients.administration.eco_system.client import EcosystemClient


class EcosystemUtils:
    def __init__(self):
        self._client = EcosystemClient()

    def get_default_environment_id(self) -> str:
        user_context = EcosystemClient().get_authenticated_user_context().user
        default_environment_id: str = (
            user_context.account_details.default_environment_id
        )
        return default_environment_id
