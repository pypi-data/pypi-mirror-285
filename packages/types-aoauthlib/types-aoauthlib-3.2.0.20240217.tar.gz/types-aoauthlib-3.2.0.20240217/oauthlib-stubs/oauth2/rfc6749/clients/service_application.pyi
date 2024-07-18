from ..parameters import prepare_token_request as prepare_token_request
from .base import Client as Client
from _typeshed import Incomplete
from oauthlib.common import to_unicode as to_unicode

class ServiceApplicationClient(Client):
    grant_type: str
    private_key: Incomplete
    subject: Incomplete
    issuer: Incomplete
    audience: Incomplete
    def __init__(self, client_id, private_key: Incomplete | None = None, subject: Incomplete | None = None, issuer: Incomplete | None = None, audience: Incomplete | None = None, **kwargs) -> None: ...
    def prepare_request_body(self, private_key: Incomplete | None = None, subject: Incomplete | None = None, issuer: Incomplete | None = None, audience: Incomplete | None = None, expires_at: Incomplete | None = None, issued_at: Incomplete | None = None, extra_claims: Incomplete | None = None, body: str = '', scope: Incomplete | None = None, include_client_id: bool = False, **kwargs): ...
