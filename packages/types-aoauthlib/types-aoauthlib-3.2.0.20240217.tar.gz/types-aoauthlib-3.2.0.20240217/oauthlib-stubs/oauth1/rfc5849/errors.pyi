from _typeshed import Incomplete
from oauthlib.common import add_params_to_uri as add_params_to_uri, urlencode as urlencode

class OAuth1Error(Exception):
    error: Incomplete
    description: str
    uri: Incomplete
    status_code: Incomplete
    def __init__(self, description: Incomplete | None = None, uri: Incomplete | None = None, status_code: int = 400, request: Incomplete | None = None) -> None: ...
    def in_uri(self, uri): ...
    @property
    def twotuples(self): ...
    @property
    def urlencoded(self): ...

class InsecureTransportError(OAuth1Error):
    error: str
    description: str

class InvalidSignatureMethodError(OAuth1Error):
    error: str

class InvalidRequestError(OAuth1Error):
    error: str

class InvalidClientError(OAuth1Error):
    error: str
