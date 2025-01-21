from .WearableDeviceDataRetriever import WearableDeviceDataRetriever
from .FitbitQueryHandler import FitbitQueryHandler
from .DataEndpointsEnum import DataEndpointsEnum
from vitals_data_retrieving.data_consumption_tools.Entities.UsersDataBase import UsersDataBase
from vitals_data_retrieving.data_consumption_tools.Entities.VitalsDataBase import VitalsDataBase
from vitals_data_retrieving.data_consumption_tools.Entities.UsersDataBase import decode_data
from vitals_data_retrieving.data_consumption_tools.Entities.ResponseCode import ResponseCode
from vitals_data_retrieving.data_consumption_tools.Entities.CryptoUtils import hash_data
from http import HTTPStatus
from dotenv import load_dotenv
from flask import jsonify
from werkzeug import Response
import os
import requests
import base64


def get_token_from_database(document_id) -> tuple[str, ResponseCode]:
    """
    Get the token from the database

    :param document_id: str: Document ID (hashed User ID)
    :return: tuple[str, ResponseCode]: Token and response code
    """
    data_base = UsersDataBase()
    response_code, document = data_base.read_document(document_id)

    if response_code == ResponseCode.ERROR_NOT_FOUND:
        return "", response_code

    decoded_document = decode_data(document)
    return decoded_document["token"], response_code


def get_all_documents() -> tuple[list, HTTPStatus]:
    """
    Retrieve all documents from the database and handle errors.

    :return: tuple[list, HTTPStatus]: List of documents and HTTP status code
    """
    data_base = UsersDataBase()
    response_code, documents = data_base.get_all_documents()

    if response_code == ResponseCode.ERROR_NOT_FOUND:
        return [], HTTPStatus.NOT_FOUND
    elif response_code == ResponseCode.ERROR_UNKNOWN:
        return [], HTTPStatus.INTERNAL_SERVER_ERROR

    return documents, HTTPStatus.OK


def get_query_error_message(operation, status_code) -> dict:
    """
    Get the error message for a query

    :param operation: str: Operation
    :param status_code: HTTPStatus: HTTP status code
    :return: dict: Error response
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

        :param authorization_code: str: Authorization code
        :return: HTTPStatus: HTTP status code
        """
        authorization_string = self.get_authorization_string()
        headers, data = self.get_request_params_for_token(authorization_string, authorization_code)
        token_response = self.make_token_request(headers, data)

        user_id = token_response.get('user_id')
        access_token = token_response.get('access_token')
        refresh_token = token_response.get('refresh_token')

        data_base = UsersDataBase()
        document_id = hash_data(user_id)

        response_code, _ = data_base.read_document(document_id)
        if response_code == ResponseCode.ERROR_NOT_FOUND:
            data_base.insert_document(user_id, access_token, refresh_token)
            status = HTTPStatus.OK
        elif response_code == ResponseCode.SUCCESS:
            data_base.update_document(document_id, access_token, refresh_token)
            status = HTTPStatus.OK
        else:
            status = HTTPStatus.INTERNAL_SERVER_ERROR
        return status

    def refresh_access_token(self, document_id) -> tuple[Response, HTTPStatus]:
        """
        Refresh the access token from the API

        :param document_id: str: Document ID (Hashed User ID)
        :return: tuple[Response, HTTPStatus]: Operation status and HTTP status code
        """
        data_base = UsersDataBase()

        response_code, document = data_base.read_document(document_id)

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

        status = data_base.update_document(document_id, new_access_token, new_refresh_token)

        if status == ResponseCode.SUCCESS:
            return jsonify({'status': 'Token refreshed successfully'}), HTTPStatus.OK
        else:
            return jsonify({'error': 'Failed to refresh token'}), HTTPStatus.INTERNAL_SERVER_ERROR

    def update_all_tokens(self) -> tuple[Response, HTTPStatus]:
        """
        Update all access tokens from the wearable device API in the database

        :arg: None
        :return: tuple[Response, HTTPStatus]: Operation status and HTTP status code
        """
        documents, status = get_all_documents()
        if status != HTTPStatus.OK:
            return jsonify(
                {'error': 'No users found' if status == HTTPStatus.NOT_FOUND else 'Unknown error occurred'}), status

        total_documents = len(documents)
        updated_tokens = 0

        for document in documents:
            decoded_document = decode_data(document)
            user_id = decoded_document["user_id"]
            _, status = self.refresh_access_token(user_id)

            if status == HTTPStatus.OK:
                updated_tokens += 1

        if updated_tokens == total_documents:
            return jsonify({'status': 'All tokens updated successfully'}), HTTPStatus.OK
        elif updated_tokens == 0:
            return jsonify({'error': 'Failed to update any tokens'}), HTTPStatus.INTERNAL_SERVER_ERROR
        else:
            return jsonify({'error': 'Some tokens failed to update'}), HTTPStatus.PARTIAL_CONTENT

    def get_user_info(self, user_id) -> tuple[Response, HTTPStatus]:
        """
        Get user info from the wearable device API

        :param user_id: str: User ID
        :return: tuple[Response, HTTPStatus]: User info and HTTP status code
        """
        document_id = hash_data(user_id)
        token, response_code = get_token_from_database(document_id)

        if response_code == ResponseCode.ERROR_NOT_FOUND:
            return jsonify({'error': 'User not found'}), HTTPStatus.NOT_FOUND

        data, status = self.make_data_query(document_id=document_id, token=token, scope=["user_info"])
        return data, status

    def retrieve_data(
            self, user_id: str = None, date: str = None, scope: list[str] = None, db_storage: bool = False) \
            -> tuple[Response, HTTPStatus]:
        """
        Retrieve data from the wearable device by querying the API

        :param user_id: str: User ID
        :param date: str: Date in 'YYYY-MM-DD' format
        :param scope: list[str]: List of data scopes to query (e.g., "sleep", "heart_rate").
        :param db_storage: bool: Store data in the database
        :return: tuple[Response, HTTPStatus]: Data and HTTP status code
        """
        document_id = hash_data(user_id)
        token, response_code = get_token_from_database(document_id)

        if response_code == ResponseCode.ERROR_NOT_FOUND:
            return jsonify({'error': 'User not found'}), HTTPStatus.NOT_FOUND

        data, status = self.make_data_query(document_id, token, date, scope, db_storage)
        return data, status

    def get_daily_vitals_data(self, date) -> tuple[Response, HTTPStatus]:
        """
        Get daily vitals data from all the users stored in the database and store it in the database

        :return: tuple[Response, HTTPStatus]: Operation status and HTTP status code
        """
        documents, status = get_all_documents()
        if status != HTTPStatus.OK:
            return jsonify(
                {'error': 'No users found' if status == HTTPStatus.NOT_FOUND else 'Unknown error occurred'}), status

        total_documents = len(documents)
        successful_operations = 0
        partial_operations = 0

        scope = ["sleep", "heart_rate", "heart_rate_variability", "breathing_rate", "spO2", "activity"]

        for document in documents:
            decoded_document = decode_data(document)
            user_id = decoded_document["user_id"]
            token = decoded_document["token"]

            _, status = self.make_data_query(document_id=user_id, token=token, date=date, scope=scope, db_storage=True)

            if status == HTTPStatus.OK:
                successful_operations += 1
            if status == HTTPStatus.PARTIAL_CONTENT:
                partial_operations += 1

        if successful_operations == total_documents:
            return jsonify({'status': 'All daily vitals data fetched successfully'}), HTTPStatus.OK
        elif partial_operations > 0:
            return jsonify({'error': 'Some daily vitals data failed to fetch'}), HTTPStatus.PARTIAL_CONTENT
        else:
            return jsonify({'error': 'Failed to fetch any daily vitals data'}), HTTPStatus.INTERNAL_SERVER_ERROR

    def make_data_query(
            self, document_id, token: str = None, date: str = None, scope: list[str] = None, db_storage: bool = False) \
            -> tuple[Response, HTTPStatus]:
        """
        Fetches data from Fitbit API for each element in the provided scope.
        Dynamically calls the associated method from FitbitQueryHandler.

        :param document_id: str: Document ID (hashed User ID).
        :param token: str: Access token for the Fitbit API.
        :param date: date: Date in 'YYYY-MM-DD' format.
        :param scope: list[str]: List of data scopes to query (e.g., "sleep", "heart_rate").
        :param db_storage: bool: Flag to store data in the database.
        :return: tuple[Response, HTTPStatus]: Combined data and HTTP status code.
        """
        try:
            query_handler = FitbitQueryHandler(token)

            combined_data = {}

            successful_operations = 0
            total_operations = len(scope)

            for element in scope:
                if element in DataEndpointsEnum.__members__:

                    status = None

                    for _ in range(3):
                        response, status = query_handler.fetch_data(element, date)

                        if status == HTTPStatus.OK:
                            combined_data[element] = response
                            successful_operations += 1
                            break
                        elif status == HTTPStatus.UNAUTHORIZED:
                            self.refresh_access_token(document_id)
                            new_token, _ = get_token_from_database(document_id)
                            query_handler.update_token(new_token)
                        else:
                            break

                    if status != HTTPStatus.OK:
                        combined_data[element] = get_query_error_message(element, status)
                else:
                    combined_data[element] = {"error": f"Operation {element} not found in FitbitQueryHandler"}

            if db_storage:
                vitals_database = VitalsDataBase()
                response = vitals_database.insert_document(document_id, date, combined_data)
            else:
                response = ResponseCode.SUCCESS

            if response == ResponseCode.SUCCESS and (successful_operations == total_operations):
                status = ResponseCode.SUCCESS
            elif successful_operations > 0:
                status = HTTPStatus.PARTIAL_CONTENT
            else:
                status = HTTPStatus.INTERNAL_SERVER_ERROR
            return jsonify(combined_data), status

        except Exception as e:
            return jsonify({'error': f"An error occurred: {str(e)}"}), HTTPStatus.INTERNAL_SERVER_ERROR

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

        :param authorization_string: str: Authorization string
        :param authorization_code: str: Authorization code
        :return: tuple[dict,dict]: Headers and data
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

        :param authorization_string: str: Authorization string
        :param refresh_token: str: Refresh token
        :return: tuple[dict,dict]: Headers and data
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

        :param headers: dict: Headers for the request
        :param data: dict: Data for the request
        :return: dict: Token request response JSON
        """
        token_response = requests.post(self.TOKEN_URL, headers=headers, data=data)
        return token_response.json()
