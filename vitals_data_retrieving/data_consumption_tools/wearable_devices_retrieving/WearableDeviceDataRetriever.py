from abc import ABCMeta, abstractmethod

class WearableDeviceDataRetriever(metaclass=ABCMeta):
    @abstractmethod
    def retrieve_data(self) -> str:
        pass
