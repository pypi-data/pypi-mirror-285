from ..errors import OAuth2Error as OAuth2Error
from .base import BaseEndpoint as BaseEndpoint, catch_errors_and_unavailability as catch_errors_and_unavailability
from _typeshed import Incomplete
from oauthlib.common import Request as Request

log: Incomplete

class IntrospectEndpoint(BaseEndpoint):
    valid_token_types: Incomplete
    valid_request_methods: Incomplete
    request_validator: Incomplete
    supported_token_types: Incomplete
    def __init__(self, request_validator, supported_token_types: Incomplete | None = None) -> None: ...
    async def create_introspect_response(self, uri, http_method: str = 'POST', body: Incomplete | None = None, headers: Incomplete | None = None): ...
    async def validate_introspect_request(self, request) -> None: ...
