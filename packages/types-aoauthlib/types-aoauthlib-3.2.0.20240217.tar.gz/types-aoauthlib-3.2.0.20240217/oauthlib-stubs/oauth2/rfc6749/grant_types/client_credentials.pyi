from .. import errors as errors
from .base import GrantTypeBase as GrantTypeBase
from _typeshed import Incomplete

log: Incomplete

class ClientCredentialsGrant(GrantTypeBase):
    async def create_token_response(self, request, token_handler): ...
    async def validate_token_request(self, request) -> None: ...
