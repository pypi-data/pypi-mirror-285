from .utils import build_path, tag_label


def test_build_path():
    row = {
        "bigflo": "oli",
        "laurel": "hardy",
        "dupond": "dupont",
    }
    keys = ["laurel", "dupond"]
    assert build_path(row, keys) == "hardy.dupont"


def test_tag_label():
    row = {
        "tag_name": "marketplace",
        "tag_value": "",
    }
    assert tag_label(row) == "marketplace"

    row = {
        "tag_name": "fi",
        "tag_value": "fou",
    }
    assert tag_label(row) == "fi:fou"
