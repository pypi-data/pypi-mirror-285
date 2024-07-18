import logging
from typing import Dict, Iterator, List, Optional

import tableauserverclient as TSC  # type: ignore
from tableauserverclient import Pager

from ....utils import SerializedAsset
from ..assets import TableauRevampAsset
from ..constants import (
    DEFAULT_PAGE_SIZE,
    DEFAULT_TIMEOUT_SECONDS,
    TABLEAU_SERVER_VERSION,
)
from .credentials import TableauRevampCredentials
from .errors import TableauApiError
from .gql_queries import FIELDS_QUERIES, GQL_QUERIES, QUERY_TEMPLATE
from .tsc_fields import TSC_FIELDS

logger = logging.getLogger(__name__)

# these assets must be extracted via TableauServerClient
_TSC_ASSETS = (
    # only users who published content can be extracted from MetadataAPI
    TableauRevampAsset.USER,
    # projects are not available in Metadata API
    TableauRevampAsset.PROJECT,
    # view count are not available in Metadata API
    TableauRevampAsset.USAGE,
)

# increase the value when extraction is too slow
# decrease the value when timeouts arise
_CUSTOM_PAGE_SIZE: Dict[TableauRevampAsset, int] = {
    # for some clients, extraction of columns tend to hit the node limit
    # https://community.tableau.com/s/question/0D54T00000YuK60SAF/metadata-query-nodelimitexceeded-error
    # the workaround is to reduce pagination
    TableauRevampAsset.COLUMN: 50,
    # fields are light but volumes are bigger
    TableauRevampAsset.FIELD: 1000,
    TableauRevampAsset.TABLE: 50,
}


def _pick_fields(
    data: Pager,
    asset: TableauRevampAsset,
) -> SerializedAsset:
    fields = TSC_FIELDS[asset]

    def _pick(row: dict):
        return {field: getattr(row, field) for field in fields}

    return [_pick(row) for row in data]


def _enrich_datasources_with_tsc(
    datasources: SerializedAsset,
    tsc_datasources: SerializedAsset,
) -> SerializedAsset:
    """
    Enrich datasources with fields coming from TableauServerClient:
    - project_luid
    - webpage_url
    """

    mapping = {row["id"]: row for row in tsc_datasources}

    for datasource in datasources:
        if datasource["__typename"] != "PublishedDatasource":
            # embedded datasources are bound to workbooks => no project
            # embedded datasources cannot be accessed via URL => no webpage_url
            continue
        luid = datasource["luid"]
        tsc_datasource = mapping[luid]
        datasource["projectLuid"] = tsc_datasource["project_id"]
        datasource["webpageUrl"] = tsc_datasource["webpage_url"]

    return datasources


def _enrich_workbooks_with_tsc(
    workbooks: SerializedAsset,
    tsc_workbooks: SerializedAsset,
) -> SerializedAsset:
    """
    Enrich workbooks with fields coming from TableauServerClient:
    - project_luid
    """

    mapping = {row["id"]: row for row in tsc_workbooks}

    for workbook in workbooks:
        luid = workbook["luid"]
        tsc_workbook = mapping.get(luid)
        if not tsc_workbook:
            # it happens that a workbook is in Metadata API but not in TSC
            # in this case, we push the workbook with default project
            logger.warning(f"Workbook {luid} was not found in TSC")
            workbook["projectLuid"] = None
            continue

        workbook["projectLuid"] = tsc_workbook["project_id"]

    return workbooks


def gql_query_scroll(
    server,
    query: str,
    resource: str,
) -> Iterator[SerializedAsset]:
    """Iterate over GQL query results, handling pagination and cursor"""

    def _call(cursor: Optional[str]) -> dict:
        # If cursor is defined it must be quoted else use null token
        token = "null" if cursor is None else f'"{cursor}"'
        query_ = query.replace("AFTER_TOKEN_SIGNAL", token)
        answer = server.metadata.query(query_)
        if "errors" in answer:
            raise TableauApiError(answer["errors"])
        return answer["data"][f"{resource}Connection"]

    cursor = None
    while True:
        payload = _call(cursor)
        yield payload["nodes"]

        page_info = payload["pageInfo"]
        if page_info["hasNextPage"]:
            cursor = page_info["endCursor"]
        else:
            break


class TableauRevampClient:
    """
    Connect to Tableau's API and extract assets.

    Relies on TableauServerClient overlay:
    https://tableau.github.io/server-client-python/docs/
    - for connection
    - to extract Users (Metadata

    Calls the MetadataAPI, using graphQL
    https://help.tableau.com/current/api/metadata_api/en-us/reference/index.html
    """

    def __init__(
        self,
        credentials: TableauRevampCredentials,
        timeout_sec: int = DEFAULT_TIMEOUT_SECONDS,
    ):
        self._credentials = credentials
        self._server = TSC.Server(self._credentials.server_url)
        options = {"verify": True, "timeout": timeout_sec}
        self._server.add_http_options(options)
        self._server.version = TABLEAU_SERVER_VERSION
        self.errors: List[str] = []

    @staticmethod
    def name() -> str:
        return "Tableau/API"

    def _user_password_login(self) -> None:
        """Login into Tableau using user and password"""
        self._server.auth.sign_in(
            TSC.TableauAuth(
                self._credentials.user,
                self._credentials.password,
                site_id=self._credentials.site_id,
            ),
        )

    def _pat_login(self) -> None:
        """Login into Tableau using personal authentication token"""
        self._server.auth.sign_in(
            TSC.PersonalAccessTokenAuth(
                self._credentials.token_name,
                self._credentials.token,
                site_id=self._credentials.site_id,
            ),
        )

    def login(self) -> None:
        """
        Depending on the given credentials, logs-in using either:
        - user/password
        - token_name/value (Personal Access Token)
        https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_auth.htm

        Raises an error if none can be found
        """

        if self._credentials.user and self._credentials.password:
            logger.info("Logging in using user and password authentication")
            return self._user_password_login()

        if self._credentials.token_name and self._credentials.token:
            logger.info("Logging in using token authentication")
            return self._pat_login()

        raise ValueError(
            "Invalid credentials: either user/password or PAT must be provided",
        )

    def base_url(self) -> str:
        return self._credentials.server_url

    def _fetch_from_tsc(
        self,
        asset: TableauRevampAsset,
    ) -> SerializedAsset:

        if asset == TableauRevampAsset.DATASOURCE:
            data = TSC.Pager(self._server.datasources)

        elif asset == TableauRevampAsset.PROJECT:
            data = TSC.Pager(self._server.projects)

        elif asset == TableauRevampAsset.USAGE:
            data = TSC.Pager(self._server.views, usage=True)

        elif asset == TableauRevampAsset.USER:
            data = TSC.Pager(self._server.users)

        elif asset == TableauRevampAsset.WORKBOOK:
            data = TSC.Pager(self._server.workbooks)

        else:
            raise AssertionError(f"Fetching from TSC not supported for {asset}")

        return _pick_fields(data, asset)

    def _run_graphql_query(
        self,
        resource: str,
        fields: str,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> SerializedAsset:
        query = QUERY_TEMPLATE.format(
            resource=resource,
            fields=fields,
            page_size=page_size,
        )
        result_pages = gql_query_scroll(self._server, query, resource)
        return [asset for page in result_pages for asset in page]

    def _fetch_fields(self) -> SerializedAsset:
        result: SerializedAsset = []
        page_size = _CUSTOM_PAGE_SIZE[TableauRevampAsset.FIELD]
        for resource, fields in FIELDS_QUERIES:
            current = self._run_graphql_query(resource, fields, page_size)
            result.extend(current)
        return result

    def _fetch_from_metadata_api(
        self,
        asset: TableauRevampAsset,
    ) -> SerializedAsset:
        if asset == TableauRevampAsset.FIELD:
            return self._fetch_fields()

        page_size = _CUSTOM_PAGE_SIZE.get(asset) or DEFAULT_PAGE_SIZE
        resource, fields = GQL_QUERIES[asset]
        return self._run_graphql_query(resource, fields, page_size)

    def _fetch_datasources(self) -> SerializedAsset:
        asset = TableauRevampAsset.DATASOURCE

        datasources = self._fetch_from_metadata_api(asset)
        datasource_projects = self._fetch_from_tsc(asset)

        return _enrich_datasources_with_tsc(datasources, datasource_projects)

    def _fetch_workbooks(self) -> SerializedAsset:
        asset = TableauRevampAsset.WORKBOOK

        workbooks = self._fetch_from_metadata_api(asset)
        workbook_projects = self._fetch_from_tsc(asset)

        return _enrich_workbooks_with_tsc(workbooks, workbook_projects)

    def fetch(
        self,
        asset: TableauRevampAsset,
    ) -> SerializedAsset:
        """
        Extract the given Tableau Asset
        """
        if asset == TableauRevampAsset.DATASOURCE:
            # both APIs are required to extract datasources
            return self._fetch_datasources()

        if asset == TableauRevampAsset.WORKBOOK:
            # both APIs are required to extract workbooks
            return self._fetch_workbooks()

        if asset in _TSC_ASSETS:
            # some assets can only be extracted via TSC
            return self._fetch_from_tsc(asset)

        # extract most assets via Metadata API
        return self._fetch_from_metadata_api(asset)
