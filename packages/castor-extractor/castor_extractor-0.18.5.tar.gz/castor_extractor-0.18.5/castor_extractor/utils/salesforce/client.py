import logging
from typing import Iterator, Optional, Tuple

from requests import Response

from ...utils.client.api import APIClient
from .constants import DEFAULT_API_VERSION, DEFAULT_PAGINATION_LIMIT
from .credentials import SalesforceCredentials

logger = logging.getLogger(__name__)


class SalesforceBaseClient(APIClient):
    """
    Salesforce API client.
    https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_rest.htm
    """

    api_version = DEFAULT_API_VERSION
    pagination_limit = DEFAULT_PAGINATION_LIMIT

    PATH_TPL = "services/data/v{version}/{suffix}"

    def __init__(self, credentials: SalesforceCredentials):
        super().__init__(host=credentials.base_url)
        self._token = self._access_token(credentials)

    def _access_token(self, credentials: SalesforceCredentials) -> str:
        url = self.build_url(self._host, "services/oauth2/token")
        response = self._call(
            url, "POST", params=credentials.token_request_payload()
        )
        return response["access_token"]

    def _full_url(self, suffix: str) -> str:
        path = self.PATH_TPL.format(version=self.api_version, suffix=suffix)
        return self.build_url(self._host, path)

    @property
    def query_url(self) -> str:
        """Returns the query API url"""
        return self._full_url("query")

    @property
    def tooling_url(self) -> str:
        """Returns the tooling API url"""
        return self._full_url("tooling/query")

    @staticmethod
    def _query_processor(response: Response) -> Tuple[dict, Optional[str]]:
        results = response.json()
        return results["records"], results.get("nextRecordsUrl")

    def _has_reached_pagination_limit(self, page_number: int) -> bool:
        return page_number > self.pagination_limit

    def _query_first_page(self, query: str) -> Tuple[Iterator[dict], str]:
        url = self.query_url
        logger.info("querying page 0")
        records, next_page_url = self._call(
            url, params={"q": query}, processor=self._query_processor
        )
        return records, next_page_url

    def _query_all(self, query: str) -> Iterator[dict]:
        """
        Run a SOQL query over salesforce API.

        more: https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm
        """
        records, next_page_path = self._query_first_page(query)
        yield from records

        page_count = 1
        while next_page_path and not self._has_reached_pagination_limit(
            page_count
        ):
            logger.info(f"querying page {page_count}")
            url = self.build_url(self._host, next_page_path)
            records, next_page_path = self._call(
                url, processor=self._query_processor
            )
            yield from records
            page_count += 1
