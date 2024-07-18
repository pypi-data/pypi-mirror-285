from typing import Iterable, List, Tuple, Union

from ...utils import (
    OUTPUT_DIR,
    current_timestamp,
    deep_serialize,
    from_env,
    get_output_filename,
    write_json,
    write_summary,
)
from .assets import METADATA_ASSETS, PowerBiAsset
from .client import Client, PowerbiCredentials


def iterate_all_data(
    client: Client,
) -> Iterable[Tuple[PowerBiAsset, Union[List, dict]]]:
    for asset in PowerBiAsset:
        if asset in METADATA_ASSETS:
            continue

        data = client.fetch(asset)
        yield asset, deep_serialize(data)


def extract_all(**kwargs) -> None:
    """
    Extract data from PowerBI REST API
    Store the output files locally under the given output_directory
    """
    _output_directory = kwargs.get("output") or from_env(OUTPUT_DIR)
    creds = PowerbiCredentials(**kwargs)
    client = Client(creds)
    ts = current_timestamp()

    for key, data in iterate_all_data(client):
        filename = get_output_filename(key.name.lower(), _output_directory, ts)
        write_json(filename, data)

    write_summary(_output_directory, ts)
