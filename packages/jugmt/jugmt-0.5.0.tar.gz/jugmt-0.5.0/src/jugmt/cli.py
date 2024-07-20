"""
Command-Line Interface
======================

Produces .html and .json when given .docx documents
"""

import json
from argparse import ArgumentParser, Namespace
from pathlib import Path

from jugmt.document import Document

SCHEMA_FILENAME = "document.figures.schema.json"


def parse_args() -> Namespace:
    """Return command-line arguments"""

    parser = ArgumentParser(
        description="Extract table information from .docx documents"
    )
    parser.add_argument(
        "document", nargs="*", type=Path, help="path to one or more .docx document(s)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="directory where the output will be saved",
        default=Path("output"),
    )
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="skip validation if this flag is set.",
    )
    parser.add_argument(
        "--dump-schema",
        action="store_true",
        help=f"write schema to f{SCHEMA_FILENAME} and exit",
    )

    args = parser.parse_args()
    if not args.document and not args.dump_schema:
        parser.error("the following arguments are required: document")

    return args


def main() -> int:
    """CLI entrypoint"""

    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    if args.dump_schema:
        with (Path.cwd() / SCHEMA_FILENAME).open("w") as schema_file:
            json.dump(Document.json_schema(), schema_file, indent=4)

    for path in args.document:
        document, errors = Document().from_docx(path)

        (args.output / path.stem).with_suffix(".html").write_text(document.to_html())

        json_str = document.to_json()
        (args.output / path.stem).with_suffix(".json").write_text(json_str)

        if not args.skip_validate:
            document.validate()

    return 0
