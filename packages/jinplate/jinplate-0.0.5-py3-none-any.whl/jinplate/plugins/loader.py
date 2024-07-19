import importlib
import os
import urllib.parse

from .filetype.base import BaseFileTypePlugin
from .scheme.base import BaseFileSchemePlugin

ENABLED_PLUGINS_SCHEME = [
    "jinplate.plugins.scheme.file",
    "jinplate.plugins.scheme.http",
]


ENABLED_PLUGINS_FILE_TYPE = [
    "jinplate.plugins.filetype.json",
    "jinplate.plugins.filetype.yaml",
    "jinplate.plugins.filetype.dotenv",
]


class DataLoader:
    """
    Filetype-agnostic loader for template values files
    """

    def __init__(self):
        self.scheme_plugins = DataLoader.load_scheme_plugins()
        self.file_type_plugins = DataLoader.load_file_type_plugins()

    def load(self, uri, file_type=None):
        """
        Loads the file at the given URI using ENABLED_PLUGINS_SCHEME and
        ENABLED_PLUGINS_FILE_TYPE

        :param uri: URI to the values file to load
        :param file_type: Override for file extension
        :return: The values as a dict
        """

        uri_parsed = urllib.parse.urlparse(uri)

        if "+" in uri_parsed.scheme:
            scheme, ext = uri_parsed.scheme.split("+", 1)
        else:
            scheme = uri_parsed.scheme
            _, ext = os.path.splitext(uri_parsed.path)
            ext = ext.lstrip(".")

        datasource_content = None
        for plugin in self.scheme_plugins:
            if plugin.scheme_matches(scheme):
                datasource_content = plugin.read(uri)
                break

        if datasource_content is None:
            raise RuntimeError(f"Unknown datasource scheme {scheme}")

        datasource_parsed = None

        if file_type is None:
            for plugin in self.file_type_plugins:
                if plugin.extension_matches(ext):
                    datasource_parsed = plugin.parse(datasource_content)
        else:
            for plugin in self.file_type_plugins:
                if plugin.extension_matches(file_type):
                    datasource_parsed = plugin.parse(datasource_content)

        if datasource_parsed is None:
            raise RuntimeError(f"Unknown datasource extension {ext}")

        return datasource_parsed

    @staticmethod
    def load_scheme_plugins() -> list[BaseFileSchemePlugin]:
        """
        Loads and returns a list of plugins responsible for loading text files based on
            their uri scheme

        :return: An instance of module.FileSchemePlugin for each module in
            ENABLED_PLUGINS_SCHEME
        """

        scheme_plugins = []

        for plugin_name in ENABLED_PLUGINS_SCHEME:
            plugin_module = importlib.import_module(plugin_name)
            plugin_cls = plugin_module.FileSchemePlugin
            scheme_plugins.append(plugin_cls())

        return scheme_plugins

    @staticmethod
    def load_file_type_plugins() -> list[BaseFileTypePlugin]:
        """
        Loads and returns a list of plugins responsible for reading text files based on
            their format

        :return: An instance of module.FileTypePlugin for each module in
            ENABLED_PLUGINS_FILE_TYPE
        """

        file_type_plugins = []

        for plugin_name in ENABLED_PLUGINS_FILE_TYPE:
            plugin_module = importlib.import_module(plugin_name)
            plugin_cls = plugin_module.FileTypePlugin
            file_type_plugins.append(plugin_cls())

        return file_type_plugins
