from .WearableDeviceDataRetriever import WearableDeviceDataRetriever

class TestDeviceDataRetriever(WearableDeviceDataRetriever):
    def __init__(self):
        pass

    def retrieve_data(self) -> str:
        return "Test Device Data"