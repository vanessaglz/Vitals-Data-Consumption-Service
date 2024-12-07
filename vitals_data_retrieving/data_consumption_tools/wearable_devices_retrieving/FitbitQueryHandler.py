from http import HTTPStatus
from typing import Tuple
from flask import session, jsonify, Response
import requests


class FitbitQueryHandler:
    def __init__(self, token: str):
        try:
            self.headers = {'Authorization': f'Bearer {token}',
                            'Accept-Language': 'en_US'}
        except KeyError:
            raise KeyError('No access token found in session')

    def get_user_info(self, start_date: str = None, end_date: str = None) -> tuple[str, HTTPStatus] | Response:
        """
        Get user info from the wearable device API
        :return: user info
        """
        try:
            # Fetch sleep data
            endpoint = f"https://api.fitbit.com/1/user/-/devices.json"
            response = requests.get(endpoint, headers=self.headers)
            formatted_response = response.json()

            return formatted_response, HTTPStatus.OK

        except Exception as e:
            return jsonify({'error': f"An error occurred during data fetch: {str(e)}"})

    def get_sleep_data(self, start_date: str = None, end_date: str = None) -> tuple[str, HTTPStatus] | Response:
        """
        Get sleep data from the wearable device API
        :return: sleep data
        """
        try:
            # Fetch sleep data
            endpoint = f"https://api.fitbit.com/1.2/user/-/sleep/date/{start_date}/{end_date}.json"
            response = requests.get(endpoint, headers=self.headers)
            formatted_response = response.json()

            return formatted_response, HTTPStatus.OK

        except Exception as e:
            return jsonify({'error': f"An error occurred during data fetch: {str(e)}"})