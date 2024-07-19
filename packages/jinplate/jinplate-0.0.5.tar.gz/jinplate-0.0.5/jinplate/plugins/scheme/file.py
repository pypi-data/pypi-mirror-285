import pathlib
import urllib.parse

from .base import BaseFileSchemePlugin


class FileSchemePlugin(BaseFileSchemePlugin):
    """
    Plugin for reading template values from file uris
    """

    def scheme_matches(self, test_scheme: str) -> bool:
        return test_scheme == "file"

    def read(self, uri: str) -> str:
        uri_parsed = urllib.parse.urlparse(uri)
        return pathlib.Path(uri_parsed.path).read_text(encoding="utf-8")
