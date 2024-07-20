import abc


class BaseFileTypePlugin(abc.ABC):
    """
    Base class for file type plugins
    """

    @abc.abstractmethod
    def extension_matches(self, test_extension: str) -> bool:
        """
        :param test_extension: Extension to test
        :return: Whether the extension should be parsed by the plugin
        """

    @abc.abstractmethod
    def parse(self, text: str):
        """
        :param text: Text to parse
        :return: Dict of values read by the plugin
        """
