"""
This module defines a wrapper class for httpx.Client to handle
authenticated HTTP requests with optional bearer token support.
"""
import httpx


class HttpxWrapper:
    """
    Wrapper around httpx.Client to provide centralized handling of
    authentication headers and request execution logic.
    """
    access_token: str | None = None

    def __init__(self, client: httpx.Client | None = None, **kwargs):
        self._client = client or httpx.Client(**kwargs)

    def _get_headers(self) -> dict[str, str]:
        return {'Authorization': f'Bearer {self.access_token}'} if self.access_token else {}

    def _handle_request(self, method: str, url: str, **kwargs):
        return getattr(self._client, method)(url, headers=self._get_headers(), **kwargs)

    def get(self, url, **kwargs):
        return self._handle_request('get', url, **kwargs)

    def post(self, url, **kwargs):
        return self._handle_request('post', url, **kwargs)

    def put(self, url, **kwargs):
        return self._handle_request('put', url, **kwargs)

    def delete(self, url, **kwargs):
        return self._handle_request('delete', url, **kwargs)

    def close(self):
        self._client.close()

    def __enter__(self):
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        return self._client.__exit__(*args)
