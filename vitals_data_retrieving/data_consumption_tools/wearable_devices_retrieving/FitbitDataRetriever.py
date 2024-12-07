from .WearableDeviceDataRetriever import WearableDeviceDataRetriever
from .FitbitQueryHandler import FitbitQueryHandler
from .DataScopeEnum import DataScopeEnum
from http import HTTPStatus
from dotenv import load_dotenv
from flask import jsonify
from requests_oauthlib import OAuth2Session
from werkzeug import Response
import os


def make_data_query(token: str = None, start_date: str = None, end_date: str = None,
                    scope: list[str] = None) -> Response:
    """
    Fetches data from Fitbit API for each element in the provided scope.
    Dynamically calls the associated method from FitbitQueryHandler.

    :param start_date: Optional start date for filtering data.
    :param end_date: Optional end date for filtering data.
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
                response, status = method(start_date, end_date)

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
        self.SCOPE = ["heartrate", "respiratory_rate", "sleep", "oxygen_saturation", "settings"]

    def get_user_info(self, token) -> Response:
        """
        Get user info from the wearable device API
        :arg: None
        :return: user info
        """
        user_info = make_data_query(token=token, scope=["user_info"])
        return user_info

    def retrieve_data(self, token: str = None, start_date: str = None, end_date: str = None,
                      scope: list[str] = None) -> Response:
        """
        Retrieve data from the wearable device by querying the API
        :arg: None
        :return: data
        """
        data = make_data_query(token, start_date, end_date, scope)
        return data

    def get_authorization_token(self, authorization_response) -> dict:
        """
        Get the authorization token
        :param authorization_response: url
        :return: authorization token
        """
        token = self.fetch_token_from_response(authorization_response)
        return token

    def connect_to_api(self) -> str:
        """
        Connect to the API by getting the authorization URL
        :arg: None
        :return: str: Authorization URL
        """
        authorization_url = self.get_authorization_url()
        return authorization_url

    def get_authorization_url(self) -> str:
        """
        Get the authorization URL
        :arg: None
        :return: str: Authorization URL
        """
        fitbit = self.create_fitbit_session()
        authorization_url, _ = fitbit.authorization_url(self.AUTHORIZATION_URL)
        return authorization_url

    def create_fitbit_session(self) -> OAuth2Session:
        """
        Uses OAuth2Session to create a session with Fitbit
        :arg: None
        :return: OAuth2Session: Fitbit session
        """
        return OAuth2Session(self.CLIENT_ID, redirect_uri=self.REDIRECT_URI, scope=self.SCOPE)

    def fetch_token_from_response(self, authorization_response) -> dict:
        """
        Fetch token from authorization response
        :param authorization_response: url
        :return: authorization token
        """
        fitbit = self.create_fitbit_session()
        token = fitbit.fetch_token(self.TOKEN_URL, authorization_response=authorization_response,
                                   client_secret=self.CLIENT_SECRET)
        return token
