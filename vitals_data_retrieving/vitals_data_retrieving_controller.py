from flask import Blueprint, request, redirect
from http import HTTPStatus

from werkzeug import Response

from vitals_data_retrieving.vitals_data_retrieving_service import VitalsDataRetrievingService
from vitals_data_retrieving.data_consumption_tools.wearable_devices_retrieving.FitbitDataRetriever import \
    FitbitDataRetriever

vitals_data_retrieving_api = Blueprint('vitals_data_retrieving_api', __name__)

# Dependencies
data_retriever = FitbitDataRetriever()


@vitals_data_retrieving_api.route('/connect_to_api')
def connect_to_api() -> Response:
    """
    Endpoint to connect to the API of the wearable device
    :return: Response: Redirect to the API login page

    Endpoint-> /vitals_data_retrieving/connect_to_api
    """
    service = VitalsDataRetrievingService(data_retriever)
    return redirect(service.get_access_to_api())


@vitals_data_retrieving_api.route('/get_vitals_data', methods=['GET'])
def get_vitals_data() -> tuple[str, HTTPStatus]:
    """
    Endpoint to get vitals data from the wearable device
    :return: tuple: Data and HTTP status code

    Endpoint-> /vitals_data_retrieving/get_vitals_data
    """
    service = VitalsDataRetrievingService(data_retriever)
    data = service.get_data_from_wearable_device_api()
    return data, HTTPStatus.OK


@vitals_data_retrieving_api.route('/callback')
def callback() -> Response:
    """
    Endpoint to handle the callback from the wearable device API
    :return: Response: Redirect to get vitals data endpoint

    Endpoint-> /vitals_data_retrieving/callback
    """
    service = VitalsDataRetrievingService(data_retriever)
    service.callback_action(request.url)
    return redirect('/vitals_data_retrieving/get_vitals_data')
