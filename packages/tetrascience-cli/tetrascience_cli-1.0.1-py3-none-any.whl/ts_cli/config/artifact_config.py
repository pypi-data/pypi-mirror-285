from typing import Optional

from ts_cli.config.cli_config import CliConfig
from ts_cli.config.interactive_config import InteractiveConfig
from ts_cli.config.util import to_version
from ts_cli.util.colour import blue, green


class ArtifactConfig(InteractiveConfig):
    """
    Artifact Configuration Abstract Class
    """

    def __init__(self, args, *, interactive: bool):
        super().__init__(args, interactive=interactive)
        self._cli_config = CliConfig(args)
        self._interactive = interactive
        self.type = None
        self.namespace = None
        self.slug = None
        self.version = None

    def _parse(self, values: dict) -> dict:
        return {
            "type": values.get("type") or None,
            "namespace": values.get("namespace") or None,
            "slug": str.lower(values.get("slug") or "") or None,
            "version": (
                to_version(values.get("version"))
                if (values.get("version") or None) is not None
                else None
            ),
            "function": values.get("function") or None,
        }

    def print(self):
        string = self.format(
            {
                "type": self.get("type"),
                "namespace": self.get("namespace"),
                "slug": self.get("slug"),
                "version": self.get("version"),
                "function": self.get("function"),
            },
            add_function=self.type == "task-script",
        )
        print(string)

    @staticmethod
    def _format_string(string: Optional[str]):
        if string:
            return green(string)
        else:
            return blue("<unset>")

    def format(self, values: dict, add_function: bool):
        values = self._parse(values)
        artifact_type = self._format_string(values.get("type"))
        namespace = self._format_string(values.get("namespace"))
        slug = self._format_string(values.get("slug"))
        version = self._format_string(values.get("version"))
        function_name = self._format_string(values.get("function"))
        function_suffix = f"@{function_name}" if add_function else ""
        return f"{artifact_type}: {namespace}/{slug}:{version}{function_suffix}"
