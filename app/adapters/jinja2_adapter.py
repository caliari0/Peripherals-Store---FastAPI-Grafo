import json
from typing import Optional

import yaml
from jinja2 import Environment

from app.core.ports.formatter_port import FormatterPort


class Jinja2Adapter(FormatterPort):
    """
    Jinja2 implementation of the formatter port.
    """

    def __init__(self):
        self.env = Environment()
        self.env.globals["enumerate"] = enumerate

    def load(
        self, path: Optional[str] = None, file_data: Optional[bytes] = None
    ) -> dict:
        """
        Loads data from a file or bytes.
        """
        if not path and not file_data:
            raise ValueError("Either path or data must be provided")
        if path and file_data:
            raise ValueError("Only one of path or data should be provided")

        loaded_data = None
        if path:
            try:
                if file_data:
                    loaded_data = yaml.safe_load(file_data.decode("utf-8"))
                else:
                    with open(path, "r") as file:
                        loaded_data = yaml.safe_load(file)
            except Exception as e:
                try:
                    if file_data:
                        loaded_data = json.loads(file_data.decode("utf-8"))
                    else:
                        with open(path, "r") as file:
                            loaded_data = json.load(file)
                except json.JSONDecodeError:
                    raise ValueError(f"Unable to load data: {e}")
        if not loaded_data:
            raise ValueError("Unable to load YAML data")
        return loaded_data

    def render(self, path: str, input: Optional[dict[str, dict]] = None) -> list[str]:
        """
        Render a template from a path and a section.
        """
        prompts = []
        data = self.load(path)
        for section, variables in (input or {}).items():
            template = self.env.from_string(data[section])
            prompt = template.render(**(variables or {}))
            prompts.append(prompt)

        return prompts
