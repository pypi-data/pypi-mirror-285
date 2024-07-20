import abc


class BaseFileSchemePlugin(abc.ABC):
    """
    Base class for file scheme plugins
    """

    @abc.abstractmethod
    def scheme_matches(self, test_scheme: str) -> bool:
        """
        :param test_scheme: Scheme to test
        :return: Whether the scheme matches a file that should be fetched by the plugin
        """

    @abc.abstractmethod
    def read(self, uri: str) -> str:
        """
        :param uri: The file to fetch and read
        :return: The text content of the file read by this plugin
        """
