from vitals_data_retrieving.data_consumption_tools.Entities.CryptoUtils import hash_data
from vitals_data_retrieving.data_consumption_tools.wearable_devices_retrieving.WearableDeviceDataRetriever import \
    WearableDeviceDataRetriever
from flask import Response
from http import HTTPStatus


class VitalsDataRetrievingService:
    def __init__(self, device_data_retriever: WearableDeviceDataRetriever):
        """
        Initialize the service with the device data retriever

        :param device_data_retriever: WearableDeviceDataRetriever: The device data retriever passed by dependency
        injection
        """
        self.device_data_retriever = device_data_retriever

    def get_access_to_api(self) -> str:
        """
        Get access to the API of the wearable device

        :arg: None
        :return: str: Authorization URL
        """
        return self.device_data_retriever.connect_to_api()

    def callback_action(self, authorization_response) -> HTTPStatus:
        """
        Handle the callback from the wearable device API

        :param authorization_response: str: URL
        :return: HTTPStatus: HTTP status code
        """
        authorization_code = authorization_response.args.get('code')  # Get the authorization code from the URL
        status = self.device_data_retriever.get_access_token(authorization_code)
        return status

    def refresh_access_token(self, user_id) -> tuple[Response, HTTPStatus]:
        """
        Refresh the access token from the wearable device API in the database

        :param user_id: str: User ID
        :return: tuple[Response, HTTPStatus]: Operation status and HTTP status code
        """
        document_id = hash_data(user_id)
        return self.device_data_retriever.refresh_access_token(document_id)

    def update_all_tokens(self) -> tuple[Response, HTTPStatus]:
        """
        Update all access tokens from the wearable device API in the database

        :return: tuple[Response, HTTPStatus]: Operation status and HTTP status code
        """
        return self.device_data_retriever.update_all_tokens()

    def get_user_info_from_api(self, user_id) -> tuple[Response, HTTPStatus]:
        """
        Get user info from the wearable device API

        :param user_id: str: User ID
        :return: tuple[Response, HTTPStatus]: User info and HTTP status code
        """
        return self.device_data_retriever.get_user_info(user_id)

    def get_data_from_wearable_device_api(
            self, user_id: str = None, date: str = None, scope: list[str] = None, db_storage: bool = False) \
            -> tuple[Response, HTTPStatus]:
        """
        Get data from the wearable device API

        :param user_id: str: User ID
        :param date: str: Date in 'YYYY-MM-DD' format
        :param scope: list[str]: List of data scopes to query (e.g., "sleep", "heart_rate").
        :param db_storage: bool: Flag to store data in the database
        :return: tuple[Response, HTTPStatus]: Data and HTTP status code
        """
        return self.device_data_retriever.retrieve_data(user_id, date, scope, db_storage)
