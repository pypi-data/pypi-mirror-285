from . import parameters as parameters, signature as signature
from _typeshed import Incomplete
from oauthlib.common import Request as Request, generate_nonce as generate_nonce, generate_timestamp as generate_timestamp, to_unicode as to_unicode, urlencode as urlencode

log: Incomplete
SIGNATURE_HMAC_SHA1: str
SIGNATURE_HMAC_SHA256: str
SIGNATURE_HMAC_SHA512: str
SIGNATURE_HMAC = SIGNATURE_HMAC_SHA1
SIGNATURE_RSA_SHA1: str
SIGNATURE_RSA_SHA256: str
SIGNATURE_RSA_SHA512: str
SIGNATURE_RSA = SIGNATURE_RSA_SHA1
SIGNATURE_PLAINTEXT: str
SIGNATURE_METHODS: Incomplete
SIGNATURE_TYPE_AUTH_HEADER: str
SIGNATURE_TYPE_QUERY: str
SIGNATURE_TYPE_BODY: str
CONTENT_TYPE_FORM_URLENCODED: str

class Client:
    SIGNATURE_METHODS: Incomplete
    @classmethod
    def register_signature_method(cls, method_name, method_callback) -> None: ...
    client_key: Incomplete
    client_secret: Incomplete
    resource_owner_key: Incomplete
    resource_owner_secret: Incomplete
    signature_method: Incomplete
    signature_type: Incomplete
    callback_uri: Incomplete
    rsa_key: Incomplete
    verifier: Incomplete
    realm: Incomplete
    encoding: Incomplete
    decoding: Incomplete
    nonce: Incomplete
    timestamp: Incomplete
    def __init__(self, client_key, client_secret: Incomplete | None = None, resource_owner_key: Incomplete | None = None, resource_owner_secret: Incomplete | None = None, callback_uri: Incomplete | None = None, signature_method=..., signature_type=..., rsa_key: Incomplete | None = None, verifier: Incomplete | None = None, realm: Incomplete | None = None, encoding: str = 'utf-8', decoding: Incomplete | None = None, nonce: Incomplete | None = None, timestamp: Incomplete | None = None) -> None: ...
    def get_oauth_signature(self, request): ...
    def get_oauth_params(self, request): ...
    def sign(self, uri, http_method: str = 'GET', body: Incomplete | None = None, headers: Incomplete | None = None, realm: Incomplete | None = None): ...
