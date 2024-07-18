from _typeshed import Incomplete
from oauthlib.common import Request as Request
from oauthlib.oauth2.rfc6749 import errors as errors
from oauthlib.oauth2.rfc6749.endpoints.base import BaseEndpoint as BaseEndpoint, catch_errors_and_unavailability as catch_errors_and_unavailability
from oauthlib.oauth2.rfc6749.tokens import BearerToken as BearerToken

log: Incomplete

class UserInfoEndpoint(BaseEndpoint):
    bearer: Incomplete
    request_validator: Incomplete
    def __init__(self, request_validator) -> None: ...
    async def create_userinfo_response(self, uri, http_method: str = 'GET', body: Incomplete | None = None, headers: Incomplete | None = None): ...
    async def validate_userinfo_request(self, request) -> None: ...
