#!/usr/bin/env python3
from pathlib import Path

from jugmt.document import Document


def test_module(tmp_path):

    paths = list(Path("documents").resolve().glob("*.docx"))
    assert len(paths) > 0, "No documents/*.docx available for testing"

    for path in paths:
        document = Document(path)
        document.extract_figures()

        json_str = document.to_json()
        assert json_str, "Failed producing a string of JSON"

        html_str = document.to_html()
        assert html_str, "Failed producing a string of HTML"

        document.validate()

        assert len(document.figures) == 2, "Unexpected about of figures in document"
