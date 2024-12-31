import base64
from typing import Tuple, Dict, Any

import requests

from .WearableDeviceDataRetriever import WearableDeviceDataRetriever
from .FitbitQueryHandler import FitbitQueryHandler
from .DataScopeEnum import DataScopeEnum
from http import HTTPStatus
from dotenv import load_dotenv
from flask import jsonify
from requests_oauthlib import OAuth2Session
from werkzeug import Response
import os


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

    def get_access_token(self, authorization_code) -> dict:
        """
        Get the authorization token

        :param authorization_code: Authorization code
        :return: authorization token
        """
        authorization_string = self.get_authorization_string()
        headers, data = self.get_request_params(authorization_string, authorization_code)
        token_response = self.make_token_request(headers, data)
        access_token = token_response.get('access_token')
        return access_token

    def get_user_info(self, token) -> Response:
        """
        Get user info from the wearable device API

        :param token: str: Authorization token
        :return: user info
        """
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

    def get_request_params(self, authorization_string, authorization_code) -> tuple[dict, dict]:
        """
        Get the request parameters

        :arg: None
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

    def make_token_request(self, headers, data) -> dict:
        """
        Make a token request to Fitbit API

        :param headers: Headers for the request
        :param data: Data for the request
        :return: Token request response JSON
        """
        token_response = requests.post(self.TOKEN_URL, headers=headers, data=data)
        return token_response.json()
