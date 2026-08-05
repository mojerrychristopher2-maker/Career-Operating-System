from abc import ABC, abstractmethod


class Plugin(ABC):

    @property
    @abstractmethod
    def name(self):
        ...

    @abstractmethod
    def initialize(self):
        ...