from .base import GrantTypeBase as GrantTypeBase
from _typeshed import Incomplete

log: Incomplete

class AuthorizationCodeGrant(GrantTypeBase):
    proxy_target: Incomplete
    def __init__(self, request_validator: Incomplete | None = None, **kwargs) -> None: ...
    async def add_id_token(self, token, token_handler, request): ...
