from .WearableDeviceDataRetriever import WearableDeviceDataRetriever
from .FitbitQueryHandler import FitbitQueryHandler
from .DataScopeEnum import DataScopeEnum
from vitals_data_retrieving.data_consumption_tools.Entities.UsersDataBase import UsersDataBase
from vitals_data_retrieving.data_consumption_tools.Entities.ResponseCode import ResponseCode
from http import HTTPStatus
from dotenv import load_dotenv
from flask import jsonify
from werkzeug import Response
from typing import Tuple, Dict, Any
import os
import requests
import base64

from ..Entities.DataCipher import DataCipher


def make_data_query(token: str = None, date: str = None, scope: list[str] = None) -> Response:
    """
    Fetches data from Fitbit API for each element in the provided scope.
    Dynamically calls the associated method from FitbitQueryHandler.

    :param token: Access token for the Fitbit API.
    :param date: Date in 'YYYY-MM-DD' format.
    :param scope: List of data scopes to query (e.g., "sleep", "heart_rate").
    :return: JSON response with combined data or error message.
    """
    try:
        # Initialize the FitbitQueryHandler
        query_handler = FitbitQueryHandler(token)

        # To store combined responses
        combined_data = {}

        # Loop through the scope and process each element
        for element in scope:
            # Get the corresponding enum value for the scope
            enum_value = DataScopeEnum[element].value

            # Dynamically call the method on the query_handler
            if hasattr(query_handler, enum_value):
                method = getattr(query_handler, enum_value)
                response, status = method(date)

                # Add the response to the combined data
                if status == HTTPStatus.OK:
                    combined_data[element] = response
                else:
                    combined_data[element] = {"error": f"Failed to fetch {element} data"}
            else:
                combined_data[element] = {"error": f"Method {enum_value} not found in FitbitQueryHandler"}

        return jsonify(combined_data)

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"})


class FitbitDataRetriever(WearableDeviceDataRetriever):
    def __init__(self):
        if os.path.exists('.env'):
            load_dotenv()
        self.CLIENT_ID = os.environ.get('CLIENT_ID')
        self.CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
        self.REDIRECT_URI = os.environ.get('REDIRECT_URI')
        self.AUTHORIZATION_URL = os.environ.get('AUTHORIZATION_URL')
        self.TOKEN_URL = os.environ.get('TOKEN_URL')
        self.SCOPE = os.environ.get('SCOPE')

    def connect_to_api(self) -> str:
        """
        Connect to the API by getting the authorization URL

        :arg: None
        :return: str: Authorization URL
        """
        authorization_url = self.get_authorization_url()
        return authorization_url

    def get_access_token(self, authorization_code) -> HTTPStatus:
        """
        Get the authorization token

        :param authorization_code: Authorization code
        :return: HTTPStatus: HTTP status code
        """
        authorization_string = self.get_authorization_string()
        headers, data = self.get_request_params_for_token(authorization_string, authorization_code)
        token_response = self.make_token_request(headers, data)

        user_id = token_response.get('user_id')
        access_token = token_response.get('access_token')
        refresh_token = token_response.get('refresh_token')

        data_base = UsersDataBase()

        response_code, _ = data_base.read_document(user_id)
        if response_code == ResponseCode.ERROR_NOT_FOUND:
            print("Inserting document")
            data_base.insert_document(user_id, access_token, refresh_token)
            status = HTTPStatus.OK
        elif response_code == ResponseCode.SUCCESS:
            print("Updating document")
            data_base.update_document(user_id, access_token, refresh_token)
            status = HTTPStatus.OK
        else:
            print("Error inserting/updating document")
            status = HTTPStatus.INTERNAL_SERVER_ERROR
        return status

    def refresh_access_token(self, refresh_token) -> Tuple[str, str]:
        """
        Refresh the access token from the API

        :param refresh_token: str: Refresh token
        :return: tuple: Access token and refresh token
        """
        authorization_string = self.get_authorization_string()
        headers, data = self.get_request_params_for_refresh_token(authorization_string, refresh_token)
        refresh_token_response = self.make_token_request(headers, data)
        access_token = refresh_token_response.get('access_token')
        new_refresh_token = refresh_token_response.get('refresh_token')
        return access_token, new_refresh_token

    def get_user_info(self, user_id) -> Response:
        """
        Get user info from the wearable device API

        :param user_id: str: User ID
        :return: user info
        """
        data_base = UsersDataBase()
        response_code, document = data_base.read_document(user_id)

        encoded_token = None

        if response_code == ResponseCode.ERROR_NOT_FOUND:
            return jsonify({'error': 'User not found'})
        elif response_code == ResponseCode.SUCCESS:
            encoded_token = document.get('token')

        cipher = DataCipher()
        decoded_token = base64.b64decode(encoded_token)
        token = cipher.decrypt(decoded_token)

        user_info = make_data_query(token=token, scope=["user_info"])
        return user_info

    def retrieve_data(self, token: str = None, date: str = None, scope: list[str] = None) -> Response:
        """
        Retrieve data from the wearable device by querying the API

        :param token: str: Authorization token
        :param date: str: Date in 'YYYY-MM-DD' format
        :param scope: List of data scopes to query (e.g., "sleep", "heart_rate").
        :return: JSON response with combined data or error message.
        """
        data = make_data_query(token, date, scope)
        return data

    def get_authorization_url(self) -> str:
        """
        Get the authorization URL

        :arg: None
        :return: str: Authorization URL
        """
        authorization_request = requests.get(self.AUTHORIZATION_URL,
                                             params={
                                                 "client_id": self.CLIENT_ID,
                                                 "response_type": "code",
                                                 "scope": self.SCOPE}
                                             )
        return authorization_request.url

    def get_authorization_string(self) -> str:
        """
        Get the authorization string

        :arg: None
        :return: str: Authorization string
        """
        raw_authorization_string = f"{self.CLIENT_ID}:{self.CLIENT_SECRET}"
        ascii_authorization_string = raw_authorization_string.encode('ascii')
        base64_authorization_string = base64.b64encode(ascii_authorization_string)
        authorization_string = base64_authorization_string.decode('ascii')
        return authorization_string

    def get_request_params_for_token(self, authorization_string, authorization_code) -> tuple[dict, dict]:
        """
        Get the request parameters for the token request

        :param authorization_string: Authorization string
        :param authorization_code: Authorization code
        :return: tuple: Headers and data
        """
        headers = {
            "authorization": f"Basic {authorization_string}",
            "accept": "application/json",
            "accept-locale": "en_US",
            "accept-language": "metric"
        }

        data = {
            "code": authorization_code,
            "client_id": self.CLIENT_ID,
            "grant_type": "authorization_code"
        }

        return headers, data

    def get_request_params_for_refresh_token(self, authorization_string, refresh_token):
        """
        Get the request parameters for the refresh token request

        :param authorization_string: Authorization string
        :param refresh_token: Refresh token
        :return: tuple: Headers and data
        """
        headers = {
            "authorization": f"Basic {authorization_string}",
            "accept": "application/json",
            "accept-locale": "en_US",
            "accept-language": "metric"
        }

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.CLIENT_ID
        }

        return headers, data

    def make_token_request(self, headers, data) -> dict:
        """
        Make a token request to Fitbit API

        :param headers: Headers for the request
        :param data: Data for the request
        :return: Token request response JSON
        """
        token_response = requests.post(self.TOKEN_URL, headers=headers, data=data)
        return token_response.json()
