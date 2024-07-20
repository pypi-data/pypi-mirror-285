#!/usr/bin/env python3
from pathlib import Path

from jugmt.document import Document


def test_module(tmp_path):

    paths = list(Path("example").resolve().glob("*.docx"))
    assert len(paths) > 0, "No documents/*.docx available for testing"

    for path in paths:
        document, errors = Document().from_docx(path)

        document_json_str = document.to_json()
        assert document_json_str, "Failed producing a string of JSON"

        document_html_str = document.to_html()
        assert document_html_str, "Failed producing a string of HTML"

        document.validate()

        assert len(document.figures) == 2, "Unexpected amouni of figures in document"
