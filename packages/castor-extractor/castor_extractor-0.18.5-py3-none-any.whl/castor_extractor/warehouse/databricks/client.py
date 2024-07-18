import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from enum import Enum
from functools import partial
from typing import Any, Dict, List, Optional, Set, Tuple, cast

import requests
from databricks import sql  # type: ignore
from requests import Response

from ...utils import (
    SafeMode,
    at_midnight,
    date_after,
    mapping_from_rows,
    retry,
    safe_mode,
)
from ...utils.client.api import APIClient
from ...utils.pager import PagerOnToken
from ..abstract.time_filter import TimeFilter
from .credentials import DatabricksCredentials
from .format import DatabricksFormatter, TagMapping
from .types import Link, Ostr, OTimestampedLink, TablesColumns, TimestampedLink
from .utils import build_path, tag_label

logger = logging.getLogger(__name__)

_DATABRICKS_CLIENT_TIMEOUT = 60
_MAX_NUMBER_OF_LINEAGE_ERRORS = 1000
_MAX_THREADS = 10
_RETRY_ATTEMPTS = 3
_RETRY_BASE_MS = 1000
_RETRY_EXCEPTIONS = [
    requests.exceptions.ConnectTimeout,
]
_WORKSPACE_ID_HEADER = "X-Databricks-Org-Id"

_INFORMATION_SCHEMA_SQL = "SELECT * FROM system.information_schema"

safe_params = SafeMode((BaseException,), _MAX_NUMBER_OF_LINEAGE_ERRORS)


class TagEntity(Enum):
    """Entities that can be tagged in Databricks"""

    COLUMN = "COLUMN"
    TABLE = "TABLE"


def _day_to_epoch_ms(day: date) -> int:
    return int(at_midnight(day).timestamp() * 1000)


def _day_hour_to_epoch_ms(day: date, hour: int) -> int:
    return int(at_midnight(day).timestamp() * 1000) + (hour * 3600 * 1000)


class LineageLinks:
    """
    helper class that handles lineage deduplication and filtering
    """

    def __init__(self):
        self.lineage: Dict[Link, Ostr] = dict()

    def add(self, timestamped_link: TimestampedLink) -> None:
        """
        keep the most recent lineage link, adding to `self.lineage`
        """
        parent, child, timestamp = timestamped_link
        link = (parent, child)
        if not self.lineage.get(link):
            self.lineage[link] = timestamp
        else:
            if not timestamp:
                return
            # keep most recent link; cast for mypy
            recent = max(cast(str, self.lineage[link]), cast(str, timestamp))
            self.lineage[link] = recent


class DatabricksClient(APIClient):
    """Databricks Client"""

    def __init__(
        self,
        credentials: DatabricksCredentials,
        db_allowed: Optional[Set[str]] = None,
        db_blocked: Optional[Set[str]] = None,
        has_table_tags: bool = False,
        has_column_tags: bool = False,
    ):
        super().__init__(host=credentials.host, token=credentials.token)
        self._http_path = credentials.http_path
        self._db_allowed = db_allowed
        self._db_blocked = db_blocked
        self._has_table_tags = has_table_tags
        self._has_column_tags = has_column_tags

        self._timeout = _DATABRICKS_CLIENT_TIMEOUT
        self.formatter = DatabricksFormatter()

    def execute_sql(
        self,
        query: str,
        params: Optional[dict] = None,
    ):
        """
        Execute a SQL query on Databricks system tables and return the results.
        https://docs.databricks.com/en/dev-tools/python-sql-connector.html

        /!\ credentials.http_path is required in order to run SQL queries
        """
        assert self._http_path, "HTTP_PATH is required to run SQL queries"
        with sql.connect(
            server_hostname=self._host,
            http_path=self._http_path,
            access_token=self._token,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    @staticmethod
    def name() -> str:
        return "Databricks"

    def _keep_catalog(self, catalog: str) -> bool:
        """
        Helper function to determine if we should keep the Databricks catalog
        which is a CastorDoc database
        """
        if self._db_allowed and catalog not in self._db_allowed:
            return False
        if self._db_blocked and catalog in self._db_blocked:
            return False
        return True

    def databases(self) -> List[dict]:
        path = "api/2.1/unity-catalog/catalogs"
        content = self.get(path=path)
        _databases = self.formatter.format_database(content.get("catalogs", []))
        return [d for d in _databases if self._keep_catalog(d["database_name"])]

    def _schemas_of_database(self, database: dict) -> List[dict]:
        path = "api/2.1/unity-catalog/schemas"
        payload = {"catalog_name": database["database_name"]}
        content = self.get(path=path, payload=payload)
        schemas = content.get("schemas", [])
        return self.formatter.format_schema(schemas, database)

    def schemas(self, databases: List[dict]) -> List[dict]:
        """
        Get the databricks schemas (also sometimes called databases)
        (which correspond to the schemas in Castor)
        leveraging the unity catalog API
        """
        return [
            schema
            for database in databases
            for schema in self._schemas_of_database(database)
        ]

    @staticmethod
    def _process_table_response(response: Response) -> Tuple[dict, str]:
        """
        Returns both the JSON content and the Workspace ID, which is found
        in the response's headers.
        """
        return response.json(), response.headers[_WORKSPACE_ID_HEADER]

    def _tables_columns_of_schema(
        self,
        schema: dict,
        table_tags: TagMapping,
        column_tags: TagMapping,
    ) -> TablesColumns:
        path = "api/2.1/unity-catalog/tables"
        payload = {
            "catalog_name": schema["database_id"],
            "schema_name": schema["schema_name"],
        }
        content, workspace_id = self.get(
            path=path,
            payload=payload,
            processor=self._process_table_response,
        )
        host = self.build_url(self._host, path="")
        return self.formatter.format_table_column(
            raw_tables=content.get("tables", []),
            schema=schema,
            host=host,
            workspace_id=workspace_id,
            table_tags=table_tags,
            column_tags=column_tags,
        )

    @staticmethod
    def _match_table_with_user(table: dict, user_mapping: dict) -> dict:
        table_owner_email = table.get("owner_email")
        if not table_owner_email:
            return table
        owner_external_id = user_mapping.get(table_owner_email)
        if not owner_external_id:
            return table
        return {**table, "owner_external_id": owner_external_id}

    def _needs_extraction(self, entity: TagEntity) -> bool:
        if entity == TagEntity.TABLE:
            return self._has_table_tags
        if entity == TagEntity.COLUMN:
            return self._has_column_tags
        raise AssertionError(f"Entity not supported: {entity}")

    def _get_tags_mapping(self, entity: TagEntity) -> TagMapping:
        """
        Fetch tags of the given entity and build a mapping:
        { path: list[tags] }

        https://docs.databricks.com/en/sql/language-manual/information-schema/table_tags.html
        https://docs.databricks.com/en/sql/language-manual/information-schema/column_tags.html
        """
        if not self._needs_extraction(entity):
            # extracting tags require additional credentials (http_path)
            return dict()

        table = f"{entity.value.lower()}_tags"
        query = f"{_INFORMATION_SCHEMA_SQL}.{table}"
        result = self.execute_sql(query)
        mapping = defaultdict(list)
        for row in result:
            dict_row = row.asDict()
            keys = ["catalog_name", "schema_name", "table_name"]
            if entity == TagEntity.COLUMN:
                keys.append("column_name")
            path = build_path(dict_row, keys)
            label = tag_label(dict_row)
            mapping[path].append(label)

        return mapping

    @staticmethod
    def _get_user_mapping(users: List[dict]) -> dict:
        return {
            **mapping_from_rows(users, "email", "id"),
            **mapping_from_rows(users, "user_name", "id"),
        }

    def tables_and_columns(
        self, schemas: List[dict], users: List[dict]
    ) -> TablesColumns:
        """
        Get the databricks tables & columns leveraging the unity catalog API
        """
        tables: List[dict] = []
        columns: List[dict] = []
        user_mapping = self._get_user_mapping(users)
        table_tags = self._get_tags_mapping(TagEntity.TABLE)
        column_tags = self._get_tags_mapping(TagEntity.COLUMN)
        for schema in schemas:

            t_to_add, c_to_add = self._tables_columns_of_schema(
                schema=schema,
                table_tags=table_tags,
                column_tags=column_tags,
            )
            t_with_owner = [
                self._match_table_with_user(table, user_mapping)
                for table in t_to_add
            ]
            tables.extend(t_with_owner)
            columns.extend(c_to_add)
        return tables, columns

    @staticmethod
    def _to_table_path(table: dict) -> Ostr:
        if table.get("name"):
            return f"{table['catalog_name']}.{table['schema_name']}.{table['name']}"
        return None

    @staticmethod
    def _to_column_path(column: dict) -> Ostr:
        if column.get("name"):
            return f"{column['catalog_name']}.{column['schema_name']}.{column['table_name']}.{column['name']}"
        return None

    def _link(
        self, path_from: Ostr, path_to: Ostr, timestamp: Ostr
    ) -> OTimestampedLink:
        """exclude missing path and self-lineage"""
        if (not path_from) or (not path_to):
            return None
        is_self_lineage = path_from.lower() == path_to.lower()
        if is_self_lineage:
            return None
        return (path_from, path_to, timestamp)

    def _single_table_lineage_links(
        self, table_path: str, single_table_lineage: dict
    ) -> List[TimestampedLink]:
        """
        process databricks lineage API response for a given table
        returns a list of (parent, child, timestamp)

        Note: in `upstreams` or `downstreams` we only care about `tableInfo`,
        we could also have `notebookInfos` or `fileInfo`
        """
        links: List[OTimestampedLink] = []
        # add parent:
        for link in single_table_lineage.get("upstreams", []):
            parent = link.get("tableInfo", {})
            parent_path = self._to_table_path(parent)
            timestamp: Ostr = parent.get("lineage_timestamp")
            links.append(self._link(parent_path, table_path, timestamp))

        # add children:
        for link in single_table_lineage.get("downstreams", []):
            child = link.get("tableInfo", {})
            child_path = self._to_table_path(child)
            timestamp = child.get("lineage_timestamp")
            links.append(self._link(table_path, child_path, timestamp))

        return list(filter(None, links))

    @safe_mode(safe_params, lambda: [])
    @retry(
        exceptions=_RETRY_EXCEPTIONS,
        max_retries=_RETRY_ATTEMPTS,
        base_ms=_RETRY_BASE_MS,
    )
    def get_single_table_lineage(
        self, table_path: str
    ) -> List[TimestampedLink]:
        """
        Helper function used in get_lineage_links.
        Call data lineage API and return the content of the result
        eg table_path: broward_prd.bronze.account_adjustments
        FYI: Maximum rate of 50 requests per SECOND
        """
        path = "api/2.0/lineage-tracking/table-lineage"
        payload = {"table_name": table_path, "include_entity_lineage": True}
        content = self.get(path=path, payload=payload)
        return self._single_table_lineage_links(table_path, content)

    def _deduplicate_lineage(self, lineages: List[TimestampedLink]) -> dict:
        deduplicated_lineage = LineageLinks()
        for timestamped_link in lineages:
            deduplicated_lineage.add(timestamped_link)
        return deduplicated_lineage.lineage

    def table_lineage(self, tables: List[dict]) -> List[dict]:
        """
        Wrapper function that retrieves all table lineage
        """
        # retrieve table lineage
        with ThreadPoolExecutor(max_workers=_MAX_THREADS) as executor:
            table_paths = [
                ".".join([table["schema_id"], table["table_name"]])
                for table in tables
            ]
            results = executor.map(self.get_single_table_lineage, table_paths)
        lineages = [link for links in results for link in links]
        deduplicated = self._deduplicate_lineage(lineages)
        return self.formatter.format_lineage(deduplicated)

    @staticmethod
    def _paths_for_column_lineage(
        tables: List[dict], columns: List[dict], table_lineage: List[dict]
    ) -> List[Tuple[str, str]]:
        """
        helper providing a list of candidate columns to look lineage for:
        we only look for column lineage where there is table lineage
        """
        # mapping between table id and its path db.schema.table
        # table["schema_id"] follows the pattern `db.schema`
        mapping = {
            table["id"]: ".".join([table["schema_id"], table["table_name"]])
            for table in tables
        }

        tables_with_lineage: Set[str] = set()
        for t in table_lineage:
            tables_with_lineage.add(t["parent_path"])
            tables_with_lineage.add(t["child_path"])

        paths_to_return: List[Tuple[str, str]] = []
        for column in columns:
            table_path = mapping[column["table_id"]]
            if table_path not in tables_with_lineage:
                continue
            column_ = (table_path, column["column_name"])
            paths_to_return.append(column_)

        return paths_to_return

    def _single_column_lineage_links(
        self, column_path: str, single_column_lineage: dict
    ) -> List[TimestampedLink]:
        """
        process databricks lineage API response for a given table
        returns a list of (parent, child, timestamp)

        Note: in `upstreams` or `downstreams` we only care about `tableInfo`,
        we could also have `notebookInfos` or `fileInfo`
        """
        links: List[OTimestampedLink] = []
        # add parent:
        for link in single_column_lineage.get("upstream_cols", []):
            parent_path = self._to_column_path(link)
            timestamp: Ostr = link.get("lineage_timestamp")
            links.append(self._link(parent_path, column_path, timestamp))

        # add children:
        for link in single_column_lineage.get("downstream_cols", []):
            child_path = self._to_column_path(link)
            timestamp = link.get("lineage_timestamp")
            links.append(self._link(column_path, child_path, timestamp))

        return list(filter(None, links))

    @safe_mode(safe_params, lambda: [])
    @retry(
        exceptions=_RETRY_EXCEPTIONS,
        max_retries=_RETRY_ATTEMPTS,
        base_ms=_RETRY_BASE_MS,
    )
    def get_single_column_lineage(
        self,
        names: Tuple[str, str],
    ) -> List[TimestampedLink]:
        """
        Helper function used in get_lineage_links.
        Call data lineage API and return the content of the result

        eg table_path: broward_prd.bronze.account_adjustments
        FYI: Maximum rate of 10 requests per SECOND
        """
        table_path, column_name = names
        api_path = "api/2.0/lineage-tracking/column-lineage"
        payload = {
            "table_name": table_path,
            "column_name": column_name,
            "include_entity_lineage": True,
        }
        content = self.get(path=api_path, payload=payload)
        column_path = f"{table_path}.{column_name}"
        return self._single_column_lineage_links(column_path, content)

    def column_lineage(
        self, tables: List[dict], columns: List[dict], table_lineage: List[dict]
    ) -> List[dict]:
        """
        Wrapper function that retrieves all column lineage
        we only try to retrieve column lineage if we found table lineage
        """
        candidate_paths = self._paths_for_column_lineage(
            tables, columns, table_lineage
        )
        lineages: List[TimestampedLink] = [
            link
            for paths in candidate_paths
            for link in self.get_single_column_lineage(paths)
        ]
        deduplicated = self._deduplicate_lineage(lineages)
        return self.formatter.format_lineage(deduplicated)

    @staticmethod
    def _time_filter(time_filter: Optional[TimeFilter]) -> dict:
        """time filter to retrieve Databricks' queries"""
        # define an explicit time window
        if not time_filter:
            time_filter = TimeFilter.default()

        assert time_filter  # for mypy

        hour_min = time_filter.hour_min
        hour_max = time_filter.hour_max
        day = time_filter.day
        if hour_min is not None and hour_max is not None:  # specific window
            start_time_ms = _day_hour_to_epoch_ms(day, hour_min)
            # note: in practice, hour_min == hour_max (hourly query ingestion)
            end_time_ms = _day_hour_to_epoch_ms(day, hour_max + 1)
        else:  # fallback to an extraction of the entire day
            start_time_ms = _day_to_epoch_ms(day)
            end_time_ms = _day_to_epoch_ms(date_after(day, 1))

        return {
            "filter_by": {
                "query_start_time_range": {
                    "end_time_ms": end_time_ms,
                    "start_time_ms": start_time_ms,
                }
            }
        }

    def query_payload(
        self,
        page_token: Optional[str] = None,
        max_results: Optional[int] = None,
        time_range_filter: Optional[dict] = None,
    ) -> dict:
        """helper method to build the payload used to retrieve queries"""
        # in payload: You can provide only one of 'page_token' or 'filter_by'
        if page_token:
            payload: Dict[str, Any] = {"page_token": page_token}
        else:
            if time_range_filter:
                payload = {**time_range_filter}
            else:
                payload = self._time_filter(None)  # default to yesterday
        if max_results:
            payload["max_results"] = max_results
        return payload

    def _scroll_queries(
        self,
        page_token: Optional[str] = None,
        max_results: Optional[int] = None,
        time_range_filter: Optional[dict] = None,
    ) -> dict:
        """
        Callback to scroll the queries api
        https://docs.databricks.com/api/workspace/queryhistory/list
        max_results: Limit the number of results returned in one page.
            The default is 100. (both on our side and Databricks')
        """
        path = "api/2.0/sql/history/queries"
        payload = self.query_payload(page_token, max_results, time_range_filter)
        content = self.get(path=path, payload=payload)
        return content if content else {}

    def queries(self, time_filter: Optional[TimeFilter] = None) -> List[dict]:
        """get all queries"""
        # add a time filter (by default: yesterday)
        time_range_filter = self._time_filter(time_filter)
        _time_filtered_scroll_queries = partial(
            self._scroll_queries,
            time_range_filter=time_range_filter,
        )

        # retrieve all queries using pagination
        raw_queries = PagerOnToken(_time_filtered_scroll_queries).all()

        return self.formatter.format_query(raw_queries)

    def users(self) -> List[dict]:
        """
        retrieve user from api
        """
        path = "api/2.0/preview/scim/v2/Users"
        content = self.get(path=path)
        return self.formatter.format_user(content.get("Resources", []))

    def _view_ddl(self, schema: dict) -> List[dict]:
        path = "api/2.1/unity-catalog/tables"
        payload = {
            "catalog_name": schema["database_id"],
            "schema_name": schema["schema_name"],
            "omit_columns": True,
        }
        content = self.get(path=path, payload=payload)
        return self.formatter.format_view_ddl(content.get("tables", []), schema)

    def view_ddl(self, schemas: List[dict]) -> List[dict]:
        """retrieve view ddl"""
        view_ddl: List[dict] = []
        for schema in schemas:
            v_to_add = self._view_ddl(schema)
            view_ddl.extend(v_to_add)
        return view_ddl
