import re
import urllib.parse
import urllib.request

from .base import BaseFileSchemePlugin


class FileSchemePlugin(BaseFileSchemePlugin):
    """
    Plugin for reading template values from http(s) uris
    """

    def scheme_matches(self, test_scheme: str) -> bool:
        return re.match(r"https?", test_scheme) is not None

    def read(self, uri: str) -> str:
        with urllib.request.urlopen(uri) as response:
            return response.read().decode("utf-8")
