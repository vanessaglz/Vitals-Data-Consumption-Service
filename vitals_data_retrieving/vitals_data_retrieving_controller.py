import os

from dotenv import load_dotenv
from flask import Blueprint, request, redirect, render_template, session
from typing import Tuple
from http import HTTPStatus

from werkzeug import Response

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
def callback() -> HTTPStatus:
    """
    Endpoint to handle the callback from the wearable device API
    :return: Response: Redirect to get vitals data endpoint

    Endpoint-> /vitals_data_retrieving/callback
    """
    service = VitalsDataRetrievingService(data_retriever)
    status = service.callback_action(request)
    return status


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
