#!/usr/bin/env python3
from pathlib import Path
from subprocess import run


def test_cli_tool(tmp_path):

    paths = list(Path("example").resolve().glob("*.docx"))
    assert len(paths) > 0, "No documents/*.docx available for testing"

    for path in paths:
        result = run(
            ["jugmt", f"{path}", "--output", str(tmp_path)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"CLI tool failed with error: {result.stderr}"
