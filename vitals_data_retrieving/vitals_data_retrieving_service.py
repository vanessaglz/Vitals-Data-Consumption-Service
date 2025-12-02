from vitals_data_retrieving.data_consumption_tools.Entities.CryptoUtils import hash_data
from vitals_data_retrieving.data_consumption_tools.wearable_devices_retrieving.WearableDeviceDataRetriever import \
    WearableDeviceDataRetriever
from flask import Response
from http import HTTPStatus
import logging
logger = logging.getLogger(__name__)


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

    def callback_action(self, request) -> tuple[dict, HTTPStatus]:
        """
        Handle the callback from the wearable device API

        :param authorization_response: str: URL
        :return: HTTPStatus: HTTP status code
        """
        authorization_code = request.args.get('code')
        if not authorization_code:
            return {"error": "missing code"}, HTTPStatus.BAD_REQUEST

        token_result, status = self.device_data_retriever.get_access_token(authorization_code)
        # Si hay error
        if status != HTTPStatus.OK:
            return token_result, status

        # token_result contiene user_id
        user_id = token_result.get("user_id")
        access_token = token_result.get("access_token")
        refresh_token = token_result.get("refresh_token")

        # para carrear el token
        try:
            # document_id = hash_data(user_id)  # ya user_id no es None
            # users_db.insert_document(document_id, access_token, refresh_token)
            return {"message": "tokens obtained", "user_id": user_id}, HTTPStatus.OK
        except Exception as e:
            logger.exception("Error guardando tokens")
            return {"error": "db error", "details": str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

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

    def get_daily_vitals_data_from_wearable_device_api(self, date) -> tuple[Response, HTTPStatus]:
        """
        Get daily vitals data from all the users stored in the database and store it in the database

        :param date: str: Date in 'YYYY-MM-DD' format
        :return: tuple[Response, HTTPStatus]: Operation status and HTTP status code
        """
        return self.device_data_retriever.get_daily_vitals_data(date)
