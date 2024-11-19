from vitals_data_retrieving.data_consumption_tools.wearable_devices_retrieving.WearableDeviceDataRetriever import WearableDeviceDataRetriever
class VitalsDataRetrievingService:
    def __init__(self, device_data_retriever: WearableDeviceDataRetriever):
        self.device_data_retriever = device_data_retriever
        pass

    def get_data_from_wearable_device_api(self) -> str:
        return self.device_data_retriever.retrieve_data()