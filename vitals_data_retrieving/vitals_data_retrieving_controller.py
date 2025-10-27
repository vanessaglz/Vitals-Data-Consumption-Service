from vitals_data_retrieving.vitals_data_retrieving_service import VitalsDataRetrievingService
from vitals_data_retrieving.data_consumption_tools.wearable_devices_retrieving.FitbitDataRetriever import \
    FitbitDataRetriever
from dotenv import load_dotenv
from flask import Blueprint, request, redirect
from http import HTTPStatus
from werkzeug import Response
from user_metrics_tracker import user_tracker
import os
import logging

logger = logging.getLogger(__name__)

vitals_data_retrieving_api = Blueprint('vitals_data_retrieving_api', __name__)

# Dependencies
data_retriever = FitbitDataRetriever()


#@vitals_data_retrieving_api.route('/connect_to_api')
@vitals_data_retrieving_api.route('/connect_to_api', methods=['GET'])
def connect_to_api() -> str:
    """
    Endpoint to connect to the API of the wearable device
    :return: Response: Redirect to the API login page

    Endpoint-> /vitals_data_retrieving/connect_to_api
    """
    #service = VitalsDataRetrievingService(data_retriever)
    #return service.get_access_to_api()
    fitbit_auth_url = (
        "https://www.fitbit.com/oauth2/authorize"
        f"?response_type=code"
        f"&client_id={os.getenv('CLIENT_ID')}"
        f"&redirect_uri={os.getenv('REDIRECT_URI')}"
        #f"&scope=activity heartrate sleep profile"
        f"&scope=activity+heartrate+sleep+profile"
        f"&prompt=consent"
        #f"&disableThirdPartyLogin=false"
    )
    return redirect(fitbit_auth_url)



@vitals_data_retrieving_api.route('/callback')
def callback() -> Response:
    """
    Endpoint to handle the callback from the wearable device API
    :return: Response: Redirect to get vitals data endpoint

    Endpoint-> /vitals_data_retrieving/callback
    """
    if os.path.exists('.env'):
        load_dotenv()
    #user_info_url = os.environ.get('USER_INFO_URL')
    service = VitalsDataRetrievingService(data_retriever)
    #service.callback_action(request)
    #return redirect(user_info_url)
    return "Autenticación completada correctamente."


@vitals_data_retrieving_api.route('/refresh_token', methods=['POST'])
def refresh_token() -> tuple[Response, HTTPStatus]:
    """
    Endpoint to refresh the access token from the wearable device API in the database
    :return: tuple[Response, HTTPStatus]: Operation status and HTTP status code

    Endpoint-> /vitals_data_retrieving/refresh_token
    """
    data = request.get_json()
    user_id = data.get('user_id')
    service = VitalsDataRetrievingService(data_retriever)
    response, status = service.refresh_access_token(user_id)
    return response, status


@vitals_data_retrieving_api.route('/update_all_tokens', methods=['POST'])
def update_all_tokens() -> tuple[Response, HTTPStatus]:
    """
    Endpoint to update all access tokens from the wearable device API in the database
    :return: tuple[Response, HTTPStatus]: Operation status and HTTP status code

    Endpoint-> /vitals_data_retrieving/update_all_tokens
    """
    service = VitalsDataRetrievingService(data_retriever)
    response, status = service.update_all_tokens()
    return response, status


@vitals_data_retrieving_api.route('/get_user_info', methods=['POST'])
@user_tracker.track_user_operation('get_user_info')
def get_user_info() -> tuple[Response, HTTPStatus]:
    """
    Endpoint to get user info from the wearable device
    :return: tuple[Response, HTTPStatus]: User info and HTTP status code

    Endpoint-> /vitals_data_retrieving/get_user_info
    """
    data = request.get_json()
    user_id = data.get('user_id')
    service = VitalsDataRetrievingService(data_retriever)
    data, status = service.get_user_info_from_api(user_id)
    return data, status


@vitals_data_retrieving_api.route('/get_vitals_data', methods=['POST'])
@user_tracker.track_user_operation('get_vitals_data')
def get_vitals_data() -> tuple[Response, HTTPStatus]:
    """
    Endpoint to get vitals data from the wearable device
    :return: tuple[Response, HTTPStatus]: Vitals data and HTTP status code

    Endpoint-> /vitals_data_retrieving/get_vitals_data
    """
    data = request.get_json()
    user_id = data.get('user_id')
    date = data.get('date')
    scope = data.get('scope')
    db_storage = data.get('db_storage', False)
    service = VitalsDataRetrievingService(data_retriever)
    data, status = service.get_data_from_wearable_device_api(user_id, date, scope, db_storage)
    return data, status


@vitals_data_retrieving_api.route('/get_daily_vitals_data', methods=['POST'])
def get_daily_vitals_data() -> tuple[Response, HTTPStatus]:
    """
    Endpoint to get daily vitals data from all the users stored in the database and store it in the database
    :return: tuple[Response, HTTPStatus]: Operation status and HTTP status code

    Endpoint-> /vitals_data_retrieving/get_daily_vitals_data
    """
    data = request.get_json()
    date = data.get('date')
    service = VitalsDataRetrievingService(data_retriever)
    response, status = service.get_daily_vitals_data_from_wearable_device_api(date)
    return response, status
