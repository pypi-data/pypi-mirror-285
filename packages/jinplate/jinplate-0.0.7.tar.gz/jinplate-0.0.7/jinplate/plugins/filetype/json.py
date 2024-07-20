import json

from .base import BaseFileTypePlugin


class FileTypePlugin(BaseFileTypePlugin):
    """
    Plugin for reading template values from JSON files
    """

    def extension_matches(self, test_extension: str) -> bool:
        return test_extension == "json"

    def parse(self, text: str):
        return json.loads(text)
