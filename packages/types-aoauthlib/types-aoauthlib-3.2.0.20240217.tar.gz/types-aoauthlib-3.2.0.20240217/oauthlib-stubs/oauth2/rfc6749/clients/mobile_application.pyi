from ..parameters import parse_implicit_response as parse_implicit_response, prepare_grant_uri as prepare_grant_uri
from .base import Client as Client
from _typeshed import Incomplete

class MobileApplicationClient(Client):
    response_type: str
    def prepare_request_uri(self, uri, redirect_uri: Incomplete | None = None, scope: Incomplete | None = None, state: Incomplete | None = None, **kwargs): ...
    token: Incomplete
    def parse_request_uri_response(self, uri, state: Incomplete | None = None, scope: Incomplete | None = None): ...
