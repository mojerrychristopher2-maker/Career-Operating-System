from abc import ABC, abstractmethod


class JobProvider(ABC):

    @abstractmethod
    def discover(self):
        """
        Returns a list of Job objects.
        """
        pass