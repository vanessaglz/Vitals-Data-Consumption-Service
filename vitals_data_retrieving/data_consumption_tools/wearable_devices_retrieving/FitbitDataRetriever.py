from .WearableDeviceDataRetriever import WearableDeviceDataRetriever
from dotenv import load_dotenv
from flask import session, jsonify
from requests_oauthlib import OAuth2Session
from werkzeug import Response
import requests
import os


def make_data_query() -> Response:
    """
    Fetches data from Fitbit API
    :arg: None
    :return: str: Success message
    """
    try:
        access_token = session['oauth_token']['access_token']
        headers = {'Authorization': f'Bearer {access_token}',
                   'Accept-Language': 'en_US'}

        # Data date range
        # start_date = "2024-11-25"
        # end_date = "2024-11-30"

        # Fetch sleep data
        sleep_url = f"https://api.fitbit.com/1/user/-/devices.json"
        sleep_response = requests.get(sleep_url, headers=headers)
        sleep_data = sleep_response.json()

        return jsonify(sleep_data)

    except Exception as e:
        return jsonify({'error': f"An error occurred during data fetch: {str(e)}"})


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

    def retrieve_data(self) -> Response:
        """
        Retrieve data from the wearable device by querying the API
        :arg: None
        :return: data
        """
        data = make_data_query()
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
