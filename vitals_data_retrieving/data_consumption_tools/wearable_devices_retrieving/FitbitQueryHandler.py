from __future__ import annotations
from .DataEndpointsEnum import DataEndpointsEnum
from http import HTTPStatus
from flask import jsonify, Response
import requests


class FitbitQueryHandler:
    def __init__(self, token: str):
        try:
            self.headers = {'Authorization': f'Bearer {token}',
                            'Accept-Language': 'en_US'}
        except KeyError:
            raise KeyError('No access token found in session')

    def update_token(self, token: str):
        self.headers['Authorization'] = f'Bearer {token}'

    def fetch_data(self, scope, date=None) -> tuple[dict, HTTPStatus]:
        """
        Fetch data based on the given scope element and optional date.

        :param scope: The scope element to fetch data for.
        :param date: Optional date in 'YYYY-MM-DD' format for endpoints that require it.
        :return: tuple: The response data and HTTP status code.
        """
        try:
            endpoint = DataEndpointsEnum[scope].value
            if "{date}" in endpoint:
                if not date:
                    return {"error": f"Date is required for {scope} operation"}, HTTPStatus.BAD_REQUEST
                endpoint = endpoint.format(date=date)

            response = requests.get(endpoint, headers=self.headers)
            return response.json(), HTTPStatus(response.status_code)

        except Exception as e:
            return {"error": f"An error occurred during data fetch: {str(e)}"}, HTTPStatus.INTERNAL_SERVER_ERROR
