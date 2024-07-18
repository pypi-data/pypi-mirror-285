from ..parameters import prepare_token_request as prepare_token_request
from .base import Client as Client
from _typeshed import Incomplete

class BackendApplicationClient(Client):
    grant_type: str
    def prepare_request_body(self, body: str = '', scope: Incomplete | None = None, include_client_id: bool = False, **kwargs): ...
