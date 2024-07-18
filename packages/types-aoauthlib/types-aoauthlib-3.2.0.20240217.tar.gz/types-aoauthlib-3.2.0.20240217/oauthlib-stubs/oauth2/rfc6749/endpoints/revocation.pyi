from ..errors import OAuth2Error as OAuth2Error
from .base import BaseEndpoint as BaseEndpoint, catch_errors_and_unavailability as catch_errors_and_unavailability
from _typeshed import Incomplete
from oauthlib.common import Request as Request

log: Incomplete

class RevocationEndpoint(BaseEndpoint):
    valid_token_types: Incomplete
    valid_request_methods: Incomplete
    request_validator: Incomplete
    supported_token_types: Incomplete
    enable_jsonp: Incomplete
    def __init__(self, request_validator, supported_token_types: Incomplete | None = None, enable_jsonp: bool = False) -> None: ...
    async def create_revocation_response(self, uri, http_method: str = 'POST', body: Incomplete | None = None, headers: Incomplete | None = None): ...
    async def validate_revocation_request(self, request) -> None: ...
