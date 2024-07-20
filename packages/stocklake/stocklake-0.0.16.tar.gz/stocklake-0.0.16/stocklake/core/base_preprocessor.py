from abc import ABC, abstractmethod


class BasePreprocessor(ABC):
    @abstractmethod
    def process(self, *args, **kwargs):
        pass
