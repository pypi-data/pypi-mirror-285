from typing import Any, Dict, Iterator, List

from .constants import SCHEMA_NAME


def _clean(raw: str) -> str:
    return raw.strip('"')


def _field_description(field: Dict[str, Any]) -> str:
    context: Dict[str, str] = {}

    field_definition: Dict[str, str] = field.get("FieldDefinition") or {}
    if description := field_definition.get("Description"):
        context["Description"] = _clean(description)
    if help_text := field.get("InlineHelpText"):
        context["Help Text"] = _clean(help_text)
    if compliance_group := field_definition.get("ComplianceGroup"):
        context["Compliance Categorization"] = _clean(compliance_group)
    if security_level := field_definition.get("SecurityClassification"):
        context["Data Sensitivity Level"] = _clean(security_level)

    return "\n".join([f"- {k}: {v}" for k, v in context.items()])


def _to_column_payload(field: dict, position: int, table_name: str) -> dict:
    field_name = field["QualifiedApiName"]
    return {
        "column_name": field_name,
        "data_type": field.get("DataType"),
        "description": _field_description(field),
        "id": f"{table_name}.{field_name}",
        "ordinal_position": position,
        "salesforce_developer_name": field.get("DeveloperName"),
        "salesforce_tooling_url": field.get("attributes", {}).get("url"),
        "table_id": table_name,
    }


def _to_table_payload(sobject: dict, table_name: str) -> dict:
    return {
        "id": table_name,
        "api_name": sobject["QualifiedApiName"],
        "label": sobject["Label"],
        "schema_id": SCHEMA_NAME,
        "table_name": table_name,
        "description": "",
        "tags": [],
        "type": "TABLE",
    }


def _merge_label_and_api_name(sobject: dict) -> dict:
    label = sobject["Label"]
    api_name = sobject["QualifiedApiName"]
    table_name = f"{label} ({api_name})"
    return _to_table_payload(sobject, table_name)


def _by_label(sobjects: List[dict]) -> Dict[str, List[dict]]:
    by_label: Dict[str, List[dict]] = dict()
    for sobject in sobjects:
        label = sobject["Label"]
        similar_sobjects = by_label.setdefault(label, [])
        similar_sobjects.append(sobject)
    return by_label


class SalesforceFormatter:
    """
    Helper functions that format the response in the format to be exported as
    csv.
    """

    @staticmethod
    def tables(sobjects: List[dict]) -> Iterator[dict]:
        """
        formats the raw list of sobjects to tables
        if two tables share the same label, then we add the api name as well
        """
        by_label = _by_label(sobjects)
        for label, similars in by_label.items():
            if len(similars) > 1:
                yield from [_merge_label_and_api_name(s) for s in similars]
            else:
                sobject = similars[0]  # unique sobject on label
                yield _to_table_payload(sobject, label)

    @staticmethod
    def columns(sobject_fields: Dict[str, List[dict]]) -> List[dict]:
        """formats the raw list of sobject fields to columns"""
        return [
            _to_column_payload(field, idx, table_name)
            for table_name, fields in sobject_fields.items()
            for idx, field in enumerate(fields)
        ]
