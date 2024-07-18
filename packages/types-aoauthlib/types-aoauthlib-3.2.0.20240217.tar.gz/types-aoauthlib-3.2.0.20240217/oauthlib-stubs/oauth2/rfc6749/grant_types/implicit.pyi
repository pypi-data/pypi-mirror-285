from .. import errors as errors
from .base import GrantTypeBase as GrantTypeBase
from _typeshed import Incomplete
from oauthlib import common as common

log: Incomplete

class ImplicitGrant(GrantTypeBase):
    response_types: Incomplete
    grant_allows_refresh_token: bool
    async def create_authorization_response(self, request, token_handler): ...
    async def create_token_response(self, request, token_handler): ...
    async def validate_authorization_request(self, request): ...
    async def validate_token_request(self, request): ...
