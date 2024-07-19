import re

import yaml

try:
    from yaml import CLoader as YamlLoader
except ImportError:
    from yaml import Loader as YamlLoader


from .base import BaseFileTypePlugin


class FileTypePlugin(BaseFileTypePlugin):
    """
    Plugin for reading template values from YAML files
    """

    def extension_matches(self, test_extension: str) -> bool:
        return re.match(r"ya?ml", test_extension) is not None

    def parse(self, text: str):
        return yaml.load(text, Loader=YamlLoader)
