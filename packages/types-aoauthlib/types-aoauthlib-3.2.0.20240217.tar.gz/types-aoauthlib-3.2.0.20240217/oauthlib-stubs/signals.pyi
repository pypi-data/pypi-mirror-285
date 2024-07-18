from _typeshed import Incomplete

signals_available: bool

class Namespace:
    def signal(self, name, doc: Incomplete | None = None): ...

class _FakeSignal:
    name: Incomplete
    __doc__: Incomplete
    def __init__(self, name, doc: Incomplete | None = None) -> None: ...
    def send(*a, **kw) -> None: ...
    connect: Incomplete
    disconnect: Incomplete
    has_receivers_for: Incomplete
    receivers_for: Incomplete
    temporarily_connected_to: Incomplete
    connected_to: Incomplete

scope_changed: Incomplete
