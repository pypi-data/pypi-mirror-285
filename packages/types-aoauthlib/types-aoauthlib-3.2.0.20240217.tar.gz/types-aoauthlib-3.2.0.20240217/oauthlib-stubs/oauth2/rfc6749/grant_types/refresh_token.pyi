from .. import errors as errors, utils as utils
from .base import GrantTypeBase as GrantTypeBase
from _typeshed import Incomplete

log: Incomplete

class RefreshTokenGrant(GrantTypeBase):
    def __init__(self, request_validator: Incomplete | None = None, issue_new_refresh_tokens: bool = True, **kwargs) -> None: ...
    async def create_token_response(self, request, token_handler): ...
    async def validate_token_request(self, request) -> None: ...
