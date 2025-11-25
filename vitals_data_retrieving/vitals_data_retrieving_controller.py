from vitals_data_retrieving.vitals_data_retrieving_service import VitalsDataRetrievingService
from vitals_data_retrieving.data_consumption_tools.wearable_devices_retrieving.FitbitDataRetriever import \
    FitbitDataRetriever
from dotenv import load_dotenv
from flask import Blueprint, request, redirect, jsonify
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
#def connect_to_api() -> str:
def connect_to_api():
    """
    Endpoint to connect to the API of the wearable device
    :return: Response: Redirect to the API login page

    Endpoint-> /vitals_data_retrieving/connect_to_api
    """
    #service = VitalsDataRetrievingService(data_retriever)
    #return service.get_access_to_api()
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    redirect_uri = os.getenv("REDIRECT_URI")

    if not client_id or not redirect_uri:
        logger.error("CLIENT_ID o REDIRECT_URI faltantes en .env")
        return jsonify({"error": "Faltan CLIENT_ID o REDIRECT_URI"}), HTTPStatus.BAD_REQUEST
    
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



@vitals_data_retrieving_api.route('/callback', methods=['GET'])
#def callback() -> Response:
def callback():
    """
    Endpoint to handle the callback from the wearable device API
    :return: Response: Redirect to get vitals data endpoint

    Endpoint-> /vitals_data_retrieving/callback
    """
    #if os.path.exists('.env'):
    #    load_dotenv()
    #user_info_url = os.environ.get('USER_INFO_URL')
    #service = VitalsDataRetrievingService(data_retriever)
    #service.callback_action(request)
    #return redirect(user_info_url)
    #return "Autenticación completada correctamente."

    try:
        load_dotenv()
        code = request.args.get('code')
        if not code:
            logger.error("Callback recibido sin 'code'")
            return jsonify({"error": "Missing authorization code"}), HTTPStatus.BAD_REQUEST
        
        service = VitalsDataRetrievingService(data_retriever)
        result, status = service.callback_action(request)
        return jsonify({"debug_code": code}), 200
    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500
        #return jsonify({
        #    "message": "Autenticación completada",
        #    "fitbit_response": result
        #}), HTTPStatus.OK

    #except Exception as e:
    #    logger.error(f"Error en callback OAuth de Fitbit: {e}")
    #    return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR


@vitals_data_retrieving_api.route('/refresh_token', methods=['POST'])
#def refresh_token() -> tuple[Response, HTTPStatus]:
def refresh_token():
    """
    Endpoint to refresh the access token from the wearable device API in the database
    :return: tuple[Response, HTTPStatus]: Operation status and HTTP status code

    Endpoint-> /vitals_data_retrieving/refresh_token
    """
    #data = request.get_json()
    #user_id = data.get('user_id')
    #service = VitalsDataRetrievingService(data_retriever)
    #response, status = service.refresh_access_token(user_id)
    #return response, status
    data = request.get_json(force=True)
    user_id = data.get('user_id')
    service = VitalsDataRetrievingService(data_retriever)
    response, status = service.refresh_access_token(user_id)
    return jsonify(response), status


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
#def get_user_info() -> tuple[Response, HTTPStatus]:
def get_user_info():
    """
    Endpoint to get user info from the wearable device
    :return: tuple[Response, HTTPStatus]: User info and HTTP status code

    Endpoint-> /vitals_data_retrieving/get_user_info
    """
    #data = request.get_json()
    #user_id = data.get('user_id')
    #service = VitalsDataRetrievingService(data_retriever)
    #data, status = service.get_user_info_from_api(user_id)
    #return data, status
    try:
        data = request.get_json(force=True)
        user_id = data.get('user_id')
        service = VitalsDataRetrievingService(data_retriever)
        user_info, status = service.get_user_info_from_api(user_id)
        return jsonify(user_info), status
    except Exception as e:
        logger.error(f"Error en get_user_info: {e}")
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR


@vitals_data_retrieving_api.route('/get_vitals_data', methods=['POST'])
@user_tracker.track_user_operation('get_vitals_data')
#def get_vitals_data() -> tuple[Response, HTTPStatus]:
def get_vitals_data():
    """
    Endpoint to get vitals data from the wearable device
    :return: tuple[Response, HTTPStatus]: Vitals data and HTTP status code

    Endpoint-> /vitals_data_retrieving/get_vitals_data
    """
    #data = request.get_json()
    #user_id = data.get('user_id')
    #date = data.get('date')
    #scope = data.get('scope')
    #db_storage = data.get('db_storage', False)
    #service = VitalsDataRetrievingService(data_retriever)
    #data, status = service.get_data_from_wearable_device_api(user_id, date, scope, db_storage)
    #return data, status
    try:
        data = request.get_json(force=True)
        user_id = data.get('user_id')
        date = data.get('date')
        scope = data.get('scope')
        db_storage = data.get('db_storage', False)

        service = VitalsDataRetrievingService(data_retriever)
        vitals, status = service.get_data_from_wearable_device_api(user_id, date, scope, db_storage)
        return jsonify(vitals), status
    except Exception as e:
        logger.error(f"Error en get_vitals_data: {e}")
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR


@vitals_data_retrieving_api.route('/get_daily_vitals_data', methods=['POST'])
#def get_daily_vitals_data() -> tuple[Response, HTTPStatus]:
def get_daily_vitals_data():

    """
    Endpoint to get daily vitals data from all the users stored in the database and store it in the database
    :return: tuple[Response, HTTPStatus]: Operation status and HTTP status code

    Endpoint-> /vitals_data_retrieving/get_daily_vitals_data
    """
    #data = request.get_json()
    #date = data.get('date')
    #service = VitalsDataRetrievingService(data_retriever)
    #response, status = service.get_daily_vitals_data_from_wearable_device_api(date)
    #return response, status
    data = request.get_json(force=True)
    date = data.get('date')
    service = VitalsDataRetrievingService(data_retriever)
    response, status = service.get_daily_vitals_data_from_wearable_device_api(date)
    return jsonify(response), status
