from typing import Dict, Tuple

from .format import (
    SCHEMA_NAME,
    SalesforceFormatter,
    _by_label,
    _field_description,
    _merge_label_and_api_name,
)


def _example_sobjects() -> Tuple[Dict[str, str], ...]:
    """Returns 4 sobjects with 2 sharing the same label"""
    a = {"Label": "a", "QualifiedApiName": "a_one"}
    b = {"Label": "b", "QualifiedApiName": "b"}
    c = {"Label": "c", "QualifiedApiName": "c"}
    a_prime = {"Label": "a", "QualifiedApiName": "a_two"}
    return a, b, c, a_prime


def test__field_description():

    field = {}
    assert _field_description(field) == ""

    definition = {}
    field = {"FieldDefinition": definition}
    assert _field_description(field) == ""

    definition.update({"Description": "foo"})
    assert "foo" in _field_description(field)

    field.update({"InlineHelpText": "bar"})
    assert "bar" in _field_description(field)

    definition.update({"ComplianceGroup": "bim"})
    assert "bim" in _field_description(field)

    definition.update({"SecurityClassification": "bam"})
    description = _field_description(field)

    assert "bam" in description
    expected = (
        "- Description: foo\n"
        "- Help Text: bar\n"
        "- Compliance Categorization: bim\n"
        "- Data Sensitivity Level: bam"
    )
    assert description == expected


def test__merge_label_and_api_name():
    sobject = {"Label": "foo", "QualifiedApiName": "bar"}
    payload = _merge_label_and_api_name(sobject)
    expected_name = "foo (bar)"
    assert payload == {
        "id": expected_name,
        "api_name": "bar",
        "label": "foo",
        "schema_id": SCHEMA_NAME,
        "table_name": expected_name,
        "description": "",
        "tags": [],
        "type": "TABLE",
    }


def test__by_label():
    a, b, c, a_prime = _example_sobjects()
    sobjects = [a, b, c, a_prime]
    by_label = _by_label(sobjects)
    assert by_label == {"a": [a, a_prime], "b": [b], "c": [c]}


def test_salesforce_formatter_tables():
    sobjects = [*_example_sobjects()]
    tables = SalesforceFormatter.tables(sobjects)
    expected_names = {"a (a_one)", "a (a_two)", "b", "c"}
    payload_names = {t["table_name"] for t in tables}
    assert payload_names == expected_names
