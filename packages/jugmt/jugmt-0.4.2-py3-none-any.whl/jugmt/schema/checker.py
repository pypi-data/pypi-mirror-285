"""

"""

import importlib.resources as pkg_resources
import json
from typing import Any, Dict

import jugmt.schema


def get_schema() -> Dict[str, Any]:
    """
    Load the stage1 JSON Schema from package datafrom return it as a dictionary.

    Returns:
        Dict[str, Any]: The JSON Schema as a dictionary.
    """

    with pkg_resources.open_text(
        jugmt.schema, "document.figures.schema.json"
    ) as content:
        return json.load(content)
