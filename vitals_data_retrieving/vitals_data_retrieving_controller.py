from flask import Blueprint, jsonify, Response, request
from http import HTTPStatus

from vitals_data_retrieving.vitals_data_retrieving_service import VitalsDataRetrievingService
from vitals_data_retrieving.data_consumption_tools.wearable_devices_retrieving.TestDeviceDataRetriever import TestDeviceDataRetriever

vitals_data_retrieving_api = Blueprint('vitals_data_retrieving_api', __name__)

data_retriever = TestDeviceDataRetriever()

@vitals_data_retrieving_api.route('', methods=['GET'])
def get_vitals_data() -> tuple[Response, int]:
    service = VitalsDataRetrievingService(data_retriever)
    data = service.get_data_from_wearable_device_api()
    return jsonify({'data': data}), HTTPStatus.OK