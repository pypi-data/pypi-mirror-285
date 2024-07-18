from _typeshed import Incomplete

log: Incomplete

class Dispatcher:
    default_grant: Incomplete
    oidc_grant: Incomplete

class AuthorizationCodeGrantDispatcher(Dispatcher):
    default_grant: Incomplete
    oidc_grant: Incomplete
    def __init__(self, default_grant: Incomplete | None = None, oidc_grant: Incomplete | None = None) -> None: ...
    async def create_authorization_response(self, request, token_handler): ...
    async def validate_authorization_request(self, request): ...

class ImplicitTokenGrantDispatcher(Dispatcher):
    default_grant: Incomplete
    oidc_grant: Incomplete
    def __init__(self, default_grant: Incomplete | None = None, oidc_grant: Incomplete | None = None) -> None: ...
    async def create_authorization_response(self, request, token_handler): ...
    async def validate_authorization_request(self, request): ...

class AuthorizationTokenGrantDispatcher(Dispatcher):
    default_grant: Incomplete
    oidc_grant: Incomplete
    request_validator: Incomplete
    def __init__(self, request_validator, default_grant: Incomplete | None = None, oidc_grant: Incomplete | None = None) -> None: ...
    async def create_token_response(self, request, token_handler): ...
