from .WearableDeviceDataRetriever import WearableDeviceDataRetriever
from .FitbitQueryHandler import FitbitQueryHandler
from .DataScopeEnum import DataScopeEnum
from vitals_data_retrieving.data_consumption_tools.Entities.UsersDataBase import UsersDataBase
from vitals_data_retrieving.data_consumption_tools.Entities.UsersDataBase import decode_data
from vitals_data_retrieving.data_consumption_tools.Entities.ResponseCode import ResponseCode
from http import HTTPStatus
from dotenv import load_dotenv
from flask import jsonify
from werkzeug import Response
import os
import requests
import base64


def get_token_from_database(user_id) -> tuple[str, ResponseCode]:
    """
    Get the token from the database

    :param user_id: str: User ID
    :return: tuple[str, ResponseCode]: Token and response code
    """
    data_base = UsersDataBase()
    response_code, document = data_base.read_document(user_id)

    if response_code == ResponseCode.ERROR_NOT_FOUND:
        return "", response_code

    decoded_document = decode_data(document)
    return decoded_document["token"], response_code


def get_query_error_message(operation, status_code) -> dict:
    """
    Get the error message for a query

    :param operation: str: Operation
    :param status_code: HTTPStatus: HTTP status code
    :return: Response: Error response
    """
    if status_code == HTTPStatus.UNAUTHORIZED:
        return {'error': f'Unauthorized access. User token has no access to {operation} data'}
    elif status_code == HTTPStatus.BAD_REQUEST:
        return {'error': f'Bad request. Failed to fetch {operation} data'}
    else:
        return {'error': f'An error occurred while fetching {operation} data'}


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
            data_base.insert_document(user_id, access_token, refresh_token)
            status = HTTPStatus.OK
        elif response_code == ResponseCode.SUCCESS:
            data_base.update_document(user_id, access_token, refresh_token)
            status = HTTPStatus.OK
        else:
            status = HTTPStatus.INTERNAL_SERVER_ERROR
        return status

    def refresh_access_token(self, user_id) -> tuple[Response, HTTPStatus]:
        """
        Refresh the access token from the API

        :param user_id: str: User ID
        :return: tuple: Operation status and HTTP status code
        """
        data_base = UsersDataBase()
        response_code, document = data_base.read_document(user_id)

        if response_code == ResponseCode.ERROR_NOT_FOUND:
            return jsonify({'error': 'User not found'}), HTTPStatus.NOT_FOUND
        elif response_code == ResponseCode.ERROR_UNKNOWN:
            return jsonify({'error': 'Unknown error occurred'}), HTTPStatus.INTERNAL_SERVER_ERROR

        decoded_document = decode_data(document)
        refresh_token = decoded_document["refresh_token"]

        authorization_string = self.get_authorization_string()
        headers, data = self.get_request_params_for_refresh_token(authorization_string, refresh_token)
        refresh_token_response = self.make_token_request(headers, data)

        new_access_token = refresh_token_response.get('access_token')
        new_refresh_token = refresh_token_response.get('refresh_token')

        status = data_base.update_document(user_id, new_access_token, new_refresh_token)

        if status == ResponseCode.SUCCESS:
            return jsonify({'status': 'Token refreshed successfully'}), HTTPStatus.OK
        else:
            return jsonify({'error': 'Failed to refresh token'}), HTTPStatus.INTERNAL_SERVER_ERROR

    def get_user_info(self, user_id) -> Response:
        """
        Get user info from the wearable device API

        :param user_id: str: User ID
        :return: user info
        """
        token, response_code = get_token_from_database(user_id)

        if response_code == ResponseCode.ERROR_NOT_FOUND:
            return jsonify({'error': 'User not found'})

        user_info = self.make_data_query(user_id=user_id, token=token, scope=["user_info"])
        return user_info

    def retrieve_data(
            self, user_id: str = None, date: str = None, scope: list[str] = None) -> tuple[Response, HTTPStatus]:
        """
        Retrieve data from the wearable device by querying the API

        :param user_id: str: User ID
        :param date: str: Date in 'YYYY-MM-DD' format
        :param scope: List of data scopes to query (e.g., "sleep", "heart_rate").
        :return: tuple: Data and HTTP status code
        """
        token, response_code = get_token_from_database(user_id)

        if response_code == ResponseCode.ERROR_NOT_FOUND:
            return jsonify({'error': 'User not found'}), HTTPStatus.NOT_FOUND

        data = self.make_data_query(user_id, token, date, scope)
        return data, HTTPStatus.OK

    def make_data_query(self, user_id, token: str = None, date: str = None, scope: list[str] = None) -> Response:
        """
        Fetches data from Fitbit API for each element in the provided scope.
        Dynamically calls the associated method from FitbitQueryHandler.

        :param user_id: str: User ID.
        :param token: Access token for the Fitbit API.
        :param date: Date in 'YYYY-MM-DD' format.
        :param scope: List of data scopes to query (e.g., "sleep", "heart_rate").
        :return: JSON response with combined data or error message.
        """
        try:
            query_handler = FitbitQueryHandler(token)

            combined_data = {}

            for element in scope:
                operation = DataScopeEnum[element].value

                # Dynamically call the method on the query_handler
                if hasattr(query_handler, operation):
                    method = getattr(query_handler, operation)

                    status = None

                    for _ in range(3):
                        response, status = method(date)

                        if status == HTTPStatus.OK:
                            combined_data[element] = response
                            break
                        elif status == HTTPStatus.UNAUTHORIZED:
                            self.refresh_access_token(user_id)
                            new_token, _ = get_token_from_database(user_id)
                            query_handler.update_token(new_token)
                        else:
                            break

                    if status != HTTPStatus.OK:
                        combined_data[element] = get_query_error_message(operation, status)
                else:
                    combined_data[element] = {"error": f"Operation {operation} not found in FitbitQueryHandler"}

            return jsonify(combined_data)

        except Exception as e:
            return jsonify({'error': f"An error occurred: {str(e)}"})

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

    def get_request_params_for_refresh_token(self, authorization_string, refresh_token) -> tuple[dict, dict]:
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
