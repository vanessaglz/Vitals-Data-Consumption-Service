from abc import ABCMeta, abstractmethod
from flask import Response


class WearableDeviceDataRetriever(metaclass=ABCMeta):

    @abstractmethod
    def connect_to_api(self) -> str:
        """
        Connect to the API of the wearable device
        :arg: None
        :return: str: Authorization string
        """
        pass

    @abstractmethod
    def get_user_info(self, token) -> str:
        """
        Get user info from the wearable device API

        :param token: str: Authorization token
        :return: str: User info
        """
        pass

    @abstractmethod
    def retrieve_data(self, token, date, scope) -> Response:
        """
        Retrieve data from the wearable device by querying the API

        :param token: str: Authorization token
        :param date: str: Date in 'YYYY-MM-DD' format
        :param scope: List of data scopes to query (e.g., "sleep", "heart_rate").
        :return: JSON response with combined data or error message.
        """
        pass

    @abstractmethod
    def get_authorization_token(self, authorization_response) -> str:
        """
        Get the authorization token from the API

        :param authorization_response: str: URL
        :return: str: Authorization token
        """
        pass
