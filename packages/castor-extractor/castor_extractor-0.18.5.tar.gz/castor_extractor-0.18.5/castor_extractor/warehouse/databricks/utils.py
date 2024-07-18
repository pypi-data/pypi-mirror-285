from typing import Dict, List


def build_path(
    row: Dict,
    keys: List[str],
) -> str:
    """
    format an asset's path:
    - picks the given keys from dict
    - join keys with a dot "."
    """
    key_values = [row[key] for key in keys]
    return ".".join(key_values)


def tag_label(row: Dict) -> str:
    """
    format the tag's label:
    - {key:value} when the value is not empty
    - {key} otherwise
    """
    tag_name = row["tag_name"]
    tag_value = row["tag_value"]
    if not tag_value:
        return tag_name
    return f"{tag_name}:{tag_value}"
