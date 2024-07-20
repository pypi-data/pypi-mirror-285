from jugmt.document import Document
from jugmt.schema.checker import get_schema


def test_check_schema_equivalence():
    dynamic_schema = Document.json_schema()
    assert dynamic_schema

    static_schema = get_schema()
    assert static_schema

    assert dynamic_schema == static_schema
