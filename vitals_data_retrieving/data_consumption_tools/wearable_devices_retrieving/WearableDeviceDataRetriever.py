from abc import ABCMeta, abstractmethod
from http import HTTPStatus
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
    def get_access_token(self, authorization_code) -> HTTPStatus:
        """
        Get the access token from the API

        :param authorization_code: str: Authorization code
        :return: HTTPStatus: HTTP status code
        """
        pass

    @abstractmethod
    def refresh_access_token(self, document_id) -> tuple[Response, HTTPStatus]:
        """
        Refresh the access token from the API

        :param document_id: str: Document ID (hashed User ID)
        :return: tuple[Response, HTTPStatus]: Operation status and HTTP status code
        """
        pass

    @abstractmethod
    def update_all_tokens(self) -> tuple[Response, HTTPStatus]:
        """
        Update all access tokens from the wearable device API in the database

        :arg: None
        :return: tuple[Response, HTTPStatus]: Operation status and HTTP status code
        """
        pass

    @abstractmethod
    def get_user_info(self, user_id) -> tuple[Response, HTTPStatus]:
        """
        Get user info from the wearable device API

        :param user_id: str: User ID
        :return: tuple[Response, HTTPStatus]: User info and HTTP status code
        """
        pass

    @abstractmethod
    def retrieve_data(self, token, date, scope, db_storage) -> tuple[Response, HTTPStatus]:
        """
        Retrieve data from the wearable device by querying the API

        :param token: str: Authorization token
        :param date: str: Date in 'YYYY-MM-DD' format
        :param scope: list[str]: List of data scopes to query (e.g., "sleep", "heart_rate").
        :param db_storage: bool: Store data in the database
        :return: tuple[Response, HTTPStatus]: Data and HTTP status code
        """
        pass

    @abstractmethod
    def get_daily_vitals_data(self, date) -> tuple[Response, HTTPStatus]:
        """
        Get daily vitals data from all the users stored in the database and store it in the database

        :param date: str: Date in 'YYYY-MM-DD' format
        :return: tuple[Response, HTTPStatus]: Operation status and HTTP status code
        """
        pass
