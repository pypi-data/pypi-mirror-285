from ..grant_types import AuthorizationCodeGrant as AuthorizationCodeGrant, ClientCredentialsGrant as ClientCredentialsGrant, ImplicitGrant as ImplicitGrant, RefreshTokenGrant as RefreshTokenGrant, ResourceOwnerPasswordCredentialsGrant as ResourceOwnerPasswordCredentialsGrant
from ..tokens import BearerToken as BearerToken
from .authorization import AuthorizationEndpoint as AuthorizationEndpoint
from .introspect import IntrospectEndpoint as IntrospectEndpoint
from .resource import ResourceEndpoint as ResourceEndpoint
from .revocation import RevocationEndpoint as RevocationEndpoint
from .token import TokenEndpoint as TokenEndpoint
from _typeshed import Incomplete

class Server(AuthorizationEndpoint, IntrospectEndpoint, TokenEndpoint, ResourceEndpoint, RevocationEndpoint):
    auth_grant: Incomplete
    implicit_grant: Incomplete
    password_grant: Incomplete
    credentials_grant: Incomplete
    refresh_grant: Incomplete
    bearer: Incomplete
    def __init__(self, request_validator, token_expires_in: Incomplete | None = None, token_generator: Incomplete | None = None, refresh_token_generator: Incomplete | None = None, *args, **kwargs) -> None: ...

class WebApplicationServer(AuthorizationEndpoint, IntrospectEndpoint, TokenEndpoint, ResourceEndpoint, RevocationEndpoint):
    auth_grant: Incomplete
    refresh_grant: Incomplete
    bearer: Incomplete
    def __init__(self, request_validator, token_generator: Incomplete | None = None, token_expires_in: Incomplete | None = None, refresh_token_generator: Incomplete | None = None, **kwargs) -> None: ...

class MobileApplicationServer(AuthorizationEndpoint, IntrospectEndpoint, ResourceEndpoint, RevocationEndpoint):
    implicit_grant: Incomplete
    bearer: Incomplete
    def __init__(self, request_validator, token_generator: Incomplete | None = None, token_expires_in: Incomplete | None = None, refresh_token_generator: Incomplete | None = None, **kwargs) -> None: ...

class LegacyApplicationServer(TokenEndpoint, IntrospectEndpoint, ResourceEndpoint, RevocationEndpoint):
    password_grant: Incomplete
    refresh_grant: Incomplete
    bearer: Incomplete
    def __init__(self, request_validator, token_generator: Incomplete | None = None, token_expires_in: Incomplete | None = None, refresh_token_generator: Incomplete | None = None, **kwargs) -> None: ...

class BackendApplicationServer(TokenEndpoint, IntrospectEndpoint, ResourceEndpoint, RevocationEndpoint):
    credentials_grant: Incomplete
    bearer: Incomplete
    def __init__(self, request_validator, token_generator: Incomplete | None = None, token_expires_in: Incomplete | None = None, refresh_token_generator: Incomplete | None = None, **kwargs) -> None: ...
