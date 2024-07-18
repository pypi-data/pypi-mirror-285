import logging
from typing import Dict, Iterator, List, Tuple

from tqdm import tqdm  # type: ignore

from ...utils.salesforce import SalesforceBaseClient, SalesforceCredentials
from .format import SalesforceFormatter
from .soql import SOBJECT_FIELDS_QUERY_TPL, SOBJECTS_QUERY_TPL

logger = logging.getLogger(__name__)


class SalesforceClient(SalesforceBaseClient):
    """
    Salesforce API client to extract sobjects
    """

    # Implicit (hard-coded in Salesforce) limitation when using SOQL of 2,000 rows
    LIMIT_RECORDS_PER_PAGE = 2000

    def __init__(self, credentials: SalesforceCredentials):
        super().__init__(credentials)
        self.formatter = SalesforceFormatter()

    @staticmethod
    def name() -> str:
        return "Salesforce"

    def _format_query(self, query_template: str, start_durable_id: str) -> str:
        return query_template.format(
            start_durable_id=start_durable_id,
            limit=self.LIMIT_RECORDS_PER_PAGE,
        )

    def _next_records(
        self, url: str, query_template: str, start_durable_id: str = "0000"
    ) -> List[dict]:
        query = self._format_query(
            query_template, start_durable_id=start_durable_id
        )
        records, _ = self._call(
            url, params={"q": query}, processor=self._query_processor
        )
        return records

    def _is_last_page(self, records: List[dict]) -> bool:
        return len(records) < self.LIMIT_RECORDS_PER_PAGE

    def _should_query_next_page(
        self, records: List[dict], page_number: int
    ) -> bool:
        return not (
            self._is_last_page(records)
            or self._has_reached_pagination_limit(page_number)
        )

    def _query_all(self, query_template: str) -> Iterator[dict]:
        """
        Run a SOQL query over salesforce API

        Note, pagination is performed via a LIMIT in the SOQL query and requires
        that ids are sorted. The SOQL query must support `limit` and
        `start_durable_id` as parameters.
        """
        url = self.query_url
        logger.info("querying page 0")
        records = self._next_records(url, query_template)
        yield from records

        page_count = 1
        while self._should_query_next_page(records, page_count):
            logger.info(f"querying page {page_count}")
            last_durable_id = records[-1]["DurableId"]
            records = self._next_records(
                url, query_template, start_durable_id=last_durable_id
            )
            yield from records
            page_count += 1

    def fetch_sobjects(self) -> List[dict]:
        """Fetch all sobjects"""
        logger.info("Extracting sobjects")
        return list(self._query_all(SOBJECTS_QUERY_TPL))

    def fetch_fields(self, sobject_name: str) -> List[dict]:
        """Fetches fields of a given sobject"""
        query = SOBJECT_FIELDS_QUERY_TPL.format(
            entity_definition_id=sobject_name
        )
        response = self._call(self.tooling_url, params={"q": query})
        return response["records"]

    def tables(self) -> List[dict]:
        """
        Get Salesforce sobjects as tables
        """
        sobjects = self.fetch_sobjects()
        logger.info(f"Extracted {len(sobjects)} sobjects")
        return list(self.formatter.tables(sobjects))

    def columns(
        self, sobject_names: List[Tuple[str, str]], show_progress: bool = True
    ) -> List[dict]:
        """
        Get salesforce sobject fields as columns
        show_progress: optionally deactivate the tqdm progress bar
        """
        sobject_fields: Dict[str, List[dict]] = dict()
        for api_name, table_name in tqdm(
            sobject_names, disable=not show_progress
        ):
            fields = self.fetch_fields(api_name)
            sobject_fields[table_name] = fields
        return self.formatter.columns(sobject_fields)
