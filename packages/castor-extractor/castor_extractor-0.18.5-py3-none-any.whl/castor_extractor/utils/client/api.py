import logging
from typing import Any, Callable, Dict, Literal, Optional

import requests

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_S = 30

# https://requests.readthedocs.io/en/latest/api/#requests.request
HttpMethod = Literal["GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"]


class APIClient:
    """
    API client
    - authentication via access token
    """

    def __init__(self, host: str, token: Optional[str] = None):
        self._host = host
        self._token = token or ""
        self._timeout = DEFAULT_TIMEOUT_S

    @staticmethod
    def build_url(host: str, path: str):
        if not host.startswith("https://"):
            host = "https://" + host
        return f"{host.strip('/')}/{path}"

    def _headers(self) -> Dict[str, str]:
        if self._token:
            return {"Authorization": f"Bearer {self._token}"}
        return dict()

    def _call(
        self,
        url: str,
        method: HttpMethod = "GET",
        *,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        processor: Optional[Callable] = None,
    ) -> Any:
        logger.debug(f"Calling {method} on {url}")
        result = requests.request(
            method,
            url,
            headers=self._headers(),
            params=params,
            json=data,
            timeout=self._timeout,
        )
        result.raise_for_status()

        if processor:
            return processor(result)

        return result.json()

    def get(
        self,
        path: str,
        payload: Optional[dict] = None,
        processor: Optional[Callable] = None,
    ) -> dict:
        """path: REST API operation path, such as /api/2.0/clusters/get"""
        url = self.build_url(self._host, path)
        return self._call(url=url, data=payload, processor=processor)
