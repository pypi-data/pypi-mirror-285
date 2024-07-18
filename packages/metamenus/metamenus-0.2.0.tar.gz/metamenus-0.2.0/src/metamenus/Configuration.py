
from logging import Logger
from logging import getLogger

from codeallybasic.SingletonV3 import SingletonV3


class Configuration(metaclass=SingletonV3):

    DEFAULT_INDENTATION:      str  = 2 * ' '
    DEFAULT_MENU_BAR_PREFIX:  str  = 'OnMB_'
    DEFAULT_MENU_PREFIX:      str  = 'OnM_'
    DEFAULT_VERBOSE_WARNINGS: bool = True

    def __init__(self):

        self.logger: Logger = getLogger(__name__)

        self._indentation:     str  = Configuration.DEFAULT_INDENTATION
        self._menuBarPrefix:   str  = Configuration.DEFAULT_MENU_BAR_PREFIX
        self._menuPrefix:      str  = Configuration.DEFAULT_MENU_PREFIX
        self._verboseWarnings: bool = Configuration.DEFAULT_VERBOSE_WARNINGS

    @property
    def indentation(self) -> str:
        """
        Indentation level for menus

        Returns:  The number of spaces that menus are indented
        """
        return self._indentation

    @indentation.setter
    def indentation(self, newValue: str):
        self._indentation = newValue

    @property
    def menuBarPrefix(self) -> str:
        """
        The prefix for the method names called on for a menu bar events

        Returns:  The prefix
        """
        return self._menuBarPrefix

    @menuBarPrefix.setter
    def menuBarPrefix(self, newValue: str):
        self._menuBarPrefix = newValue

    @property
    def menuPrefix(self) -> str:
        """
        The prefix for the method names call on menu events

        Returns: The prefix
        """
        return self._menuPrefix

    @menuPrefix.setter
    def menuPrefix(self, newValue: str):
        self._menuPrefix = newValue

    @property
    def verboseWarnings(self) -> bool:
        """
        metamenus prints messages warning about methods not found on parent if
        this value is `True`,  otherwise it is silent

        Returns: `True` if verbosity is on, else `False`
        """
        return self._verboseWarnings

    @verboseWarnings.setter
    def verboseWarnings(self, newValue: bool):
        self._verboseWarnings = newValue
