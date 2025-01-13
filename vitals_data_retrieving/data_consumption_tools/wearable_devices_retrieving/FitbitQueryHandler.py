from __future__ import annotations

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

    def get_user_info(self, date: str = None) -> tuple[str, HTTPStatus] | Response:
        """
        Get user info from the wearable device API

        :arg: None
        :return: user info
        """
        try:
            # Endpoint for User Info data
            endpoint = f"https://api.fitbit.com/1/user/-/devices.json"
            response = requests.get(endpoint, headers=self.headers)
            formatted_response = response.json()

            return formatted_response, HTTPStatus.OK

        except Exception as e:
            return jsonify({'error': f"An error occurred during data fetch: {str(e)}"})

    def get_sleep_data(self, date: str = None) -> tuple[str, HTTPStatus] | Response:
        """
        Get user's sleep log entries for a given date. The detail level: duration (minutes), efficiency, minutes of
        the sleep stages (deep, light, rem, wake)

        :param date: Date in 'YYYY-MM-DD' format.
        :return: sleep data
        """
        try:
            # Endpoint for Sleep Log by Date data
            endpoint = f"https://api.fitbit.com/1.2/user/-/sleep/date/{date}.json"
            response = requests.get(endpoint, headers=self.headers)
            formatted_response = response.json()

            return formatted_response, HTTPStatus.OK

        except Exception as e:
            return jsonify({'error': f"An error occurred during data fetch: {str(e)}"})

    def get_heart_rate_data(self, date: str = None) -> tuple[str, HTTPStatus] | Response:
        """
        Get heart rate data for a specific second from the wearable device API.

        :param date: Date in 'YYYY-MM-DD' format.
        :return: Heart rate data for the specified second.
        """
        try:
            # Endpoint for Heart Rate Intraday by Date data
            endpoint = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date}/1d/1sec.json"
            response = requests.get(endpoint, headers=self.headers)
            formatted_response = response.json()

            return formatted_response, HTTPStatus.OK

        except Exception as e:
            return jsonify({'error': f"An error occurred during data fetch: {str(e)}"})

    def get_heart_rate_variability_data(self, date: str = None) -> tuple[str, HTTPStatus] | Response:
        """
        Get heart rate variability data for a specific second from the wearable device API.

        :param date: Date in 'YYYY-MM-DD' format.
        :return: Heart rate data for the specified second.
        """
        try:
            # Endpoint for Heart Rate Variability Intraday by Date data
            endpoint = f"https://api.fitbit.com/1/user/-/hrv/date/{date}/all.json"
            response = requests.get(endpoint, headers=self.headers)
            formatted_response = response.json()

            return formatted_response, HTTPStatus.OK

        except Exception as e:
            return jsonify({'error': f"An error occurred during data fetch: {str(e)}"})
        
    def get_breathing_rate_data(self, date: str = None) -> tuple[str, HTTPStatus] | Response:
        """
        Get respiratory rate intraday data for a specific date.
        Calculates average respiratory rate and classifies rates by sleep stages.

        :param date: Date for the data (format YYYY-MM-DD).
        :return: Respiratory rate data and classification by sleep stages.
        """
        try:
            # Endpoint for Breathing Rate Intraday by Date data
            endpoint = f"https://api.fitbit.com/1/user/-/br/date/{date}/all.json"
            response = requests.get(endpoint, headers=self.headers)
            formatted_response = response.json()
            
            return formatted_response, HTTPStatus.OK

        except Exception as e:
            return jsonify({'error': f"An error occurred during data fetch: {str(e)}"})
    
    def get_oxygen_saturation_data(self, date: str = None) -> tuple[str, HTTPStatus] | Response:
        """
        Get intraday SpO2 (oxygen saturation) data for a specific date.
        Calculates average SpO2 and provides detailed data at 1-second intervals.

        :param date: Date for the data (format YYYY-MM-DD).
        :return: SpO2 data with average and detailed measurements.
        """
        try:
            
            # Endpoint for SpO2 Intraday by Date data
            endpoint = f"https://api.fitbit.com/1/user/-/spo2/date/{date}/all.json"
            response = requests.get(endpoint, headers=self.headers)
            formatted_response = response.json()

            return formatted_response, HTTPStatus.OK

        except Exception as e:
            return jsonify({'error': f"An error occurred during data fetch: {str(e)}"})
        
    def get_activity_data(self, date: str = None) -> tuple[str, HTTPStatus] | Response:
        """
        GGet intraday activity time series data (steps) for a specific date.
        Provides detailed step counts at 1-minute intervals.
        :param date: Date for the data (format YYYY-MM-DD).
        :return: Step count data with detailed measurements at 1-minute intervals.
        
        """
        try:
            # Endpoint for activity steps data
            endpoint = f"https://api.fitbit.com/1/user/-/activities/steps/date/{date}/1d/1min.json"
            response = requests.get(endpoint, headers=self.headers)
            formatted_response = response.json()
            
            return formatted_response, HTTPStatus.OK

        except Exception as e:
            return jsonify({'error': f"An error occurred during data fetch: {str(e)}"})
