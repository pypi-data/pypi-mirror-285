from .. import errors as errors
from .base import BaseEndpoint as BaseEndpoint
from _typeshed import Incomplete

log: Incomplete

class SignatureOnlyEndpoint(BaseEndpoint):
    def validate_request(self, uri, http_method: str = 'GET', body: Incomplete | None = None, headers: Incomplete | None = None): ...
