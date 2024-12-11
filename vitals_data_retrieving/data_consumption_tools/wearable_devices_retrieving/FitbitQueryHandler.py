from __future__ import annotations

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

    def get_user_info(self) -> tuple[str, HTTPStatus] | Response:
        """
        Get user info from the wearable device API

        :arg: None
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
        
    def get_breathing_rate(self, date: str = None) -> tuple[dict, HTTPStatus] | Response:
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
            
            # Process respiratory rate data
            respiratory_rate_data = formatted_response['respiratoryRate']
            avg_rate = sum(item['value'] for item in respiratory_rate_data) / len(respiratory_rate_data)
            
            # Classify data by sleep stage
            stages = {"awake": [], "light": [], "deep": [], "rem": []}
            for item in respiratory_rate_data:
                stage = item.get('sleepStage', 'unknown')  # Handle missing stages
                stages[stage].append(item['value'])
                
            # Calculate average by stage
            stage_avg = {stage: sum(values) / len(values) if values else 0 for stage, values in stages.items()}
            
            result = {
                "average_respiratory_rate": avg_rate,
                "respiratory_rate_by_sleep_stage": stage_avg
            }

            return result, HTTPStatus.OK

        except Exception as e:
            return jsonify({'error': f"An error occurred during data fetch: {str(e)}"})
    
    def get_oxygen_saturation(self, date: str = None) -> tuple[dict, HTTPStatus] | Response:
        """
        Get intraday SpO2 (oxygen saturation) data for a specific date.
        Calculates average SpO2 and provides detailed data at 1-second intervals.

        :param date: Date for the data (format YYYY-MM-DD).
        :return: SpO2 data with average and detailed measurements.
        """
        try:
            
            # Endpoint for SpO2 Intraday by Date data
            endpoint = f"https://api.fitbit.com/1/user/-/spo2/date/{date}/1sec.json"
            response = requests.get(endpoint, headers=self.headers)
            formatted_response = response.json()
            
            spo2_data = formatted_response['spo2']
            avg_spo2 = sum(item['value'] for item in spo2_data) / len(spo2_data)
            
            # Extract detailed measurements (1-second intervals)
            detailed_data = [{"time": item['time'], "value": item['value']} for item in spo2_data]
            
            result = {
                "average_spo2": avg_spo2,
                "detailed_spo2_data": detailed_data
            }

            return result, HTTPStatus.OK

        except Exception as e:
            return jsonify({'error': f"An error occurred during data fetch: {str(e)}"})
        
    def get_activity_steps(self, date: str = None) -> tuple[dict, HTTPStatus] | Response:
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
            
            step_data = formatted_response['activities-steps-intraday']['dataset']
            total_steps = sum(item['value'] for item in step_data)
            
            # Extract detailed measurements (1-minute intervals)
            detailed_data = [{"time": item['time'], "value": item['value']} for item in step_data]
            
            result = {
                "total_steps": total_steps,
                "detailed_step_data": detailed_data
            }

            return result, HTTPStatus.OK

        except Exception as e:
            return jsonify({'error': f"An error occurred during data fetch: {str(e)}"})