from _typeshed import Incomplete
from oauthlib.common import add_params_to_uri as add_params_to_uri, urlencode as urlencode

class OAuth2Error(Exception):
    error: Incomplete
    status_code: int
    description: str
    uri: Incomplete
    state: Incomplete
    redirect_uri: Incomplete
    client_id: Incomplete
    scopes: Incomplete
    response_type: Incomplete
    response_mode: Incomplete
    grant_type: Incomplete
    def __init__(self, description: Incomplete | None = None, uri: Incomplete | None = None, state: Incomplete | None = None, status_code: Incomplete | None = None, request: Incomplete | None = None) -> None: ...
    def in_uri(self, uri): ...
    @property
    def twotuples(self): ...
    @property
    def urlencoded(self): ...
    @property
    def json(self): ...
    @property
    def headers(self): ...

class TokenExpiredError(OAuth2Error):
    error: str

class InsecureTransportError(OAuth2Error):
    error: str
    description: str

class MismatchingStateError(OAuth2Error):
    error: str
    description: str

class MissingCodeError(OAuth2Error):
    error: str

class MissingTokenError(OAuth2Error):
    error: str

class MissingTokenTypeError(OAuth2Error):
    error: str

class FatalClientError(OAuth2Error): ...

class InvalidRequestFatalError(FatalClientError):
    error: str

class InvalidRedirectURIError(InvalidRequestFatalError):
    description: str

class MissingRedirectURIError(InvalidRequestFatalError):
    description: str

class MismatchingRedirectURIError(InvalidRequestFatalError):
    description: str

class InvalidClientIdError(InvalidRequestFatalError):
    description: str

class MissingClientIdError(InvalidRequestFatalError):
    description: str

class InvalidRequestError(OAuth2Error):
    error: str

class MissingResponseTypeError(InvalidRequestError):
    description: str

class MissingCodeChallengeError(InvalidRequestError):
    description: str

class MissingCodeVerifierError(InvalidRequestError):
    description: str

class AccessDeniedError(OAuth2Error):
    error: str

class UnsupportedResponseTypeError(OAuth2Error):
    error: str

class UnsupportedCodeChallengeMethodError(InvalidRequestError):
    description: str

class InvalidScopeError(OAuth2Error):
    error: str

class ServerError(OAuth2Error):
    error: str

class TemporarilyUnavailableError(OAuth2Error):
    error: str

class InvalidClientError(FatalClientError):
    error: str
    status_code: int

class InvalidGrantError(OAuth2Error):
    error: str
    status_code: int

class UnauthorizedClientError(OAuth2Error):
    error: str

class UnsupportedGrantTypeError(OAuth2Error):
    error: str

class UnsupportedTokenTypeError(OAuth2Error):
    error: str

class InvalidTokenError(OAuth2Error):
    error: str
    status_code: int
    description: str

class InsufficientScopeError(OAuth2Error):
    error: str
    status_code: int
    description: str

class ConsentRequired(OAuth2Error):
    error: str

class LoginRequired(OAuth2Error):
    error: str

class CustomOAuth2Error(OAuth2Error):
    error: Incomplete
    def __init__(self, error, *args, **kwargs) -> None: ...

def raise_from_error(error, params: Incomplete | None = None) -> None: ...
