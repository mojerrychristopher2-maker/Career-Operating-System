from abc import ABC, abstractmethod


class BaseProvider(ABC):

    """
    Base class for every job board provider.
    """

    @abstractmethod
    def discover(self):

        """
        Return a list of jobs.
        """

        pass