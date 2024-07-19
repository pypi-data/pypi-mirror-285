import io

import dotenv

from .base import BaseFileTypePlugin


class FileTypePlugin(BaseFileTypePlugin):
    """
    Plugin for reading template values from dotenv files
    """

    def extension_matches(self, test_extension: str) -> bool:
        return test_extension == "env"

    def parse(self, text: str):
        with io.StringIO(text) as stream:
            return dotenv.dotenv_values(stream=stream)
