from vitals_data_retrieving.data_consumption_tools.wearable_devices_retrieving.WearableDeviceDataRetriever import \
    WearableDeviceDataRetriever
from flask import session, Response


class VitalsDataRetrievingService:
    def __init__(self, device_data_retriever: WearableDeviceDataRetriever):
        """
        Initialize the service with the device data retriever

        :param device_data_retriever: WearableDeviceDataRetriever: The device data retriever passed by dependency injection
        """
        self.device_data_retriever = device_data_retriever

    def get_access_to_api(self) -> str:
        """
        Get access to the API of the wearable device

        :arg: None
        :return: str: Authorization URL
        """
        return self.device_data_retriever.connect_to_api()

    def get_user_info_from_api(self, token) -> str:
        """
        Get user info from the wearable device API

        :return: str: User info
        """
        return self.device_data_retriever.get_user_info(token)

    def get_data_from_wearable_device_api(
            self, token: str = None, date: str = None, scope: list[str] = None) -> Response:
        """
        Get data from the wearable device API

        :param token: str: Authorization token
        :param date: str: Date in 'YYYY-MM-DD' format
        :param scope: List of data scopes to query (e.g., "sleep", "heart_rate").
        :return: str: Data
        """
        return self.device_data_retriever.retrieve_data(token, date, scope)

    def callback_action(self, authorization_response) -> str:
        """
        Handle the callback from the wearable device API

        :param authorization_response: str: URL
        :return: str: Access token
        """
        authorization_code = authorization_response.args.get('code')  # Get the authorization code from the URL
        access_token = self.device_data_retriever.get_access_token(authorization_code)
        return access_token
