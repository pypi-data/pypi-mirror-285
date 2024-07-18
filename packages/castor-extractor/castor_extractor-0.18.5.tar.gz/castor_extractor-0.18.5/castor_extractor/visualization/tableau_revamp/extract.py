import logging
from typing import Iterable, Tuple

from ...utils import (
    OUTPUT_DIR,
    current_timestamp,
    deep_serialize,
    from_env,
    get_output_filename,
    write_errors_logs,
    write_json,
    write_summary,
)
from .assets import TableauRevampAsset
from .client import TableauRevampClient

logger = logging.getLogger(__name__)


def iterate_all_data(
    client: TableauRevampClient,
) -> Iterable[Tuple[TableauRevampAsset, list]]:
    """Iterate over the extracted Data from Tableau"""

    logger.info("Extracting USER from Tableau API")
    yield TableauRevampAsset.USER, deep_serialize(
        client.fetch(TableauRevampAsset.USER)
    )


def extract_all(client: TableauRevampClient, **kwargs: str) -> None:
    """
    Extract Data from tableau
    Store data locally in files under the output_directory
    If errors from Tableau's API are catch store them locally in file under the output_directory
    """
    output_directory = kwargs.get("output_directory") or from_env(OUTPUT_DIR)

    timestamp = current_timestamp()

    for key, data in iterate_all_data(client):
        filename = get_output_filename(key.value, output_directory, timestamp)
        write_json(filename, data)

    write_summary(
        output_directory,
        timestamp,
        base_url=client.base_url(),
        client_name=client.name(),
    )

    if client.errors:
        write_errors_logs(output_directory, timestamp, client.errors)
