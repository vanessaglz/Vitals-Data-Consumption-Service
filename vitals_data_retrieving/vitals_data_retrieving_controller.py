import os

from dotenv import load_dotenv
from flask import Blueprint, request, redirect, render_template, session
from typing import Tuple
from http import HTTPStatus
import pymongo
from werkzeug import Response

from vitals_data_retrieving.data_consumption_tools.Entities.ResponseCode import ResponseCode
from vitals_data_retrieving.vitals_data_retrieving_service import VitalsDataRetrievingService
from vitals_data_retrieving.data_consumption_tools.wearable_devices_retrieving.FitbitDataRetriever import \
    FitbitDataRetriever

vitals_data_retrieving_api = Blueprint('vitals_data_retrieving_api', __name__)

# Dependencies
data_retriever = FitbitDataRetriever()


@vitals_data_retrieving_api.route('/connect_to_api')
def connect_to_api() -> str:
    """
    Endpoint to connect to the API of the wearable device
    :return: Response: Redirect to the API login page

    Endpoint-> /vitals_data_retrieving/connect_to_api
    """
    service = VitalsDataRetrievingService(data_retriever)
    return service.get_access_to_api()


@vitals_data_retrieving_api.route('/callback')
def callback() -> Response:
    """
    Endpoint to handle the callback from the wearable device API
    :return: Response: Redirect to get vitals data endpoint

    Endpoint-> /vitals_data_retrieving/callback
    """
    if os.path.exists('.env'):
        load_dotenv()
    user_info_url = os.environ.get('USER_INFO_URL')
    service = VitalsDataRetrievingService(data_retriever)
    service.callback_action(request)
    return redirect(user_info_url)


@vitals_data_retrieving_api.route('/get_user_info', methods=['POST'])
def get_user_info() -> tuple[str, HTTPStatus]:
    """
    Endpoint to get user info from the wearable device
    :return: tuple: User info and HTTP status code

    Endpoint-> /vitals_data_retrieving/get_user_info
    """
    data = request.get_json()
    token = data.get('token')
    service = VitalsDataRetrievingService(data_retriever)
    user_info = service.get_user_info_from_api(token)
    return user_info, HTTPStatus.OK


@vitals_data_retrieving_api.route('/get_vitals_data', methods=['POST'])
def get_vitals_data() -> tuple[Response, HTTPStatus]:
    """
    Endpoint to get vitals data from the wearable device
    :return: tuple: Data and HTTP status code

    Endpoint-> /vitals_data_retrieving/get_vitals_data
    """
    data = request.get_json()
    token = data.get('token')
    date = data.get('date')
    scope = data.get('scope')
    service = VitalsDataRetrievingService(data_retriever)
    data = service.get_data_from_wearable_device_api(token, date, scope)
    return data, HTTPStatus.OK


@vitals_data_retrieving_api.route('/upload_token', methods=['POST'])
def upload_token() -> tuple[str, HTTPStatus]:
    """
    Endpoint to upload the token to the database
    :return: tuple: Data and HTTP status code

    Endpoint-> /vitals_data_retrieving/upload_token
    """
    data = request.get_json()
    user_id = data.get('user_id')
    token = data.get('token')
    refresh_token = data.get('refresh_token')

    if os.path.exists('.env'):
        load_dotenv()
    CONNECTION_STRING = os.environ.get('CONNECTION_STRING')
    DATABASE_NAME = os.environ.get('DATABASE_NAME')
    COLLECTION_NAME = os.environ.get('COLLECTION_NAME')

    client = pymongo.MongoClient(CONNECTION_STRING)
    try:
        client.server_info()
    except pymongo.errors.ServerSelectionTimeoutError:
        raise TimeoutError("Invalid API for MongoDB connection string or timed out when attempting to connect")

    database = client[DATABASE_NAME]
    collection = database[COLLECTION_NAME]

    try:
        collection.insert_one({
            "_id": user_id,
            "token": token,
            "refresh_token": refresh_token
        })
        return "Success", HTTPStatus.OK
    except pymongo.errors.DuplicateKeyError:
        return "Duplicate key", HTTPStatus.BAD_REQUEST
    except Exception as e:
        print(f"Error inserting document: {e}")
        return "Error", HTTPStatus.INTERNAL_SERVER_ERROR
