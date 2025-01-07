# stdlib
from contextlib import ContextDecorator
from typing import Optional, Type

# thirdparty
from httpx import Client


class HTTPXClient:
    client: Optional[Client]
    host: str
    entry_point: str
    base_url: str

    def __init__(self, host=None, entry_point=None):
        self.client = Client()  # timeout=Timeout(timeout=5000))
        self.host = host
        self.entry_point = entry_point
        self.base_url = f"{host}{entry_point}"

    def destructor(self):
        self.client.close()


class HTTPXContextManager(ContextDecorator):
    def __init__(self, service_client: Type[HTTPXClient], *args, host=None):
        self._service_client = service_client
        self._service_client_instance = None
        self._host = host

        super().__init__()

    def __enter__(self) -> HTTPXClient:
        self._service_client_instance = self._service_client()
        return self._service_client_instance

    def __exit__(self, type, value, traceback):
        self._service_client_instance.destructor()


httpx_context_manager = HTTPXContextManager
