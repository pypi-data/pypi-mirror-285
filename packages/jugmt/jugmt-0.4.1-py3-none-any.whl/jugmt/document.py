"""
Encapsulation of Document meta-data, .docx

Assumptions
===========

* Every NVMe specification document has a TOC with a List of figures
"""

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import docx
from docx.table import Table
from jinja2 import Environment, PackageLoader, select_autoescape
from jsonschema import validate

from jugmt.schema.checker import get_schema

REGEX_FIGURE_IDENTIFIER = (
    r"(?P<title>Figure\s+(?P<figure_nr>\d+):(?P<description>.*)\s)(?P<page_nr>\d+)"
)

TEMPLATE_HTML = "document.html.jinja2"


def table_to_dict(table: Table) -> List[List[Dict[str, Any]]]:
    """
    Returns a JSON serializable form of the given docx.table.Table.

    The table is represented as a list-of-lists, thus, it can be irregular. This is
    intentional, as the tables coming from the input can be irregular, thus, we need the
    representation to do a lint check for this.
    """

    rows = []
    for row in table.rows:
        cols = []
        for cell in row.cells:
            cols.append(
                {
                    "text": str(cell.text),
                    "tables": [
                        table_to_dict(nested_table) for nested_table in cell.tables
                    ],
                }
            )
        rows.append(cols)

    return rows


@dataclass
class Figure(object):
    """
    A figure as represented in the NVMe specification documents.
    """

    figure_nr: int  # Figure as numbered in the specification document
    page_nr: int  # The page, in the document, that the figure starts on
    title: str  # The entire figure title
    description: str  # The part of figure title without the "Fig X:" prefix

    table: Optional[List[List[Dict[str, Any]]]] = None


class Document(object):
    """
    Wrapper of the docx.Document with additional path meta-data and figures with tabular
    data converted to a JSON serializable format
    """

    def __init__(self, path: Path):
        self.path = path
        self.docx = docx.Document(path)
        self.figures: List[Any] = []

    def extract_figures(self):
        """
        Populate self.figures with figures, and their associated tabular data when
        available, found in self.docx
        """

        # Convert all tables to serializable format, and when doing so, built a map of
        #
        #   figure-description => figure
        #
        # By doing so, then lookup for the matching the figure is much faster
        tables = {}  # map "description" => "table"
        for docx_table in self.docx.tables:
            key = ("".join(docx_table.rows[0].cells[0].text.split(":")[1:])).strip()
            tables[key] = table_to_dict(docx_table)

        prev = cur = None
        for paragraph in self.docx.paragraphs:
            cur = paragraph.style.name

            # We exit early to avoid scanning the entire document, since we known that
            # once we are looking at a "table of figures" paragraph, then once we see
            # one that is not, then no more will arrive
            if prev == "table of figures" and cur != "table of figures":
                break
            prev = cur

            # Skip paragraphs before "table of figures"
            if paragraph.style.name != "table of figures":
                continue

            # Check whether the paragraph is a reference to a figure
            text = paragraph.text.strip()
            match = re.match(REGEX_FIGURE_IDENTIFIER, text)
            if not match:
                continue

            # Construct figure and lookup whether a table exists for it
            figure = Figure(
                figure_nr=int(match.group("figure_nr")),
                page_nr=int(match.group("page_nr")),
                title=match.group("title").strip(),
                description=match.group("description").strip(),
            )
            figure.table = tables.get(figure.description, None)

            self.figures.append(figure)

    def to_html(self) -> str:
        """Returns the document as a HTML-formatted string"""

        env = Environment(
            loader=PackageLoader("jugmt", "templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )
        template = env.get_template(TEMPLATE_HTML)

        return template.render(document=self)

    def to_json(self) -> str:
        """Returns the document as a JSON-formatted string"""

        return json.dumps(
            {
                "path": str(self.path),
                "figures": [asdict(fig) for fig in self.figures],
            },
            indent="\t",
        )

    def validate(self):
        """Validate the document using the schema and the Draft202012 Validator"""

        json_str = self.to_json()
        schema = get_schema()

        validate(
            instance=json.loads(json_str),
            schema=schema,
        )
