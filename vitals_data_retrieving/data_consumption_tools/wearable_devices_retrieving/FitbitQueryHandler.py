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
    def get_heart_rate_data(self, start_date: str = None, end_date: str = None, time: str = None) -> tuple[str, HTTPStatus] | Response:
        """
        Get heart rate data for a specific second from the wearable device API.
        :param date: Date in 'YYYY-MM-DD' format.
        :param time: Time in 'HH:mm:ss' format.
        :return: Heart rate data for the specified second.
        """
        try:
            # Fetch sleep |data
            endpoint = f"https://api.fitbit.com/1/user/-/activities/heart/date/{start_date}/1d/1sec/time/{time}/{time}.json"
            response = requests.get(endpoint, headers=self.headers)
            formatted_response = response.json()

            return formatted_response, HTTPStatus.OK

        except Exception as e:
            return jsonify({'error': f"An error occurred during data fetch: {str(e)}"})
        
    def get_resting_heart_rate(self, date: str = None, detail_level: str = "1min") -> tuple[dict, HTTPStatus] | Response:
        """
        Get resting heart rate data from the wearable device API.
        :param date: Date in 'YYYY-MM-DD' format.
        :param detail_level: Level of detail for the data ('1sec' or '1min').
        :return: Resting heart rate data with the specified detail level.
        """
        try:
            if detail_level not in ["1sec", "1min"]:
                raise ValueError("Detail level must be '1sec' or '1min'.")
            
            endpoint = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date}/1d/{detail_level}.json"
            response = requests.get(endpoint, headers=self.headers)
            formatted_response = response.json()
            
            resting_heart_rate = formatted_response.get("activities-heart", [{}])[0].get("value", {}).get("restingHeartRate", None)
            
            result = {
                "restingHeartRate": resting_heart_rate,
                "details": formatted_response.get("activities-heart-intraday", {})
            }

            return result, HTTPStatus.OK

        except Exception as ve:
            return jsonify({'error': str(ve)})
        except Exception as e:
            return jsonify({'error': f"An error occurred during data fetch: {str(e)}"})
        
    def get_respiratory_rate(self, date: str) -> tuple[dict, HTTPStatus] | Response:
        """
        Get respiratory rate intraday data for a specific date.
        Calculates average respiratory rate and classifies rates by sleep stages.
        :param date: Date for the data (format YYYY-MM-DD).
        :return: Respiratory rate data and classification by sleep stages.
        """
        try:
            endpoint = f"https://api.fitbit.com/1/user/-/respiratoryRate/date/{date}/all.json"
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
    
    def get_oxygen_saturation(self, date: str) -> tuple[dict, HTTPStatus] | Response:
        """
        Get intraday SpO2 (oxygen saturation) data for a specific date.
        Calculates average SpO2 and provides detailed data at 1-second intervals.
        :param date: Date for the data (format YYYY-MM-DD).
        :return: SpO2 data with average and detailed measurements.
        """
        try:
            
            # Endpoint for SpO2 data
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
        
    def get_activity_steps(self, date: str) -> tuple[dict, HTTPStatus] | Response:
        """
        GGet intraday activity time series data (steps) for a specific date.
        Provides detailed step counts at 1-minute intervals.
        :param date: Date for the data (format YYYY-MM-DD).
        :return: Step count data with detailed measurements at 1-minute intervals.
        
        """
        try:
            # Endpoint for activity steps data
            endpoint = f"https://api.fitbit.com/1/user/-/activities/steps/date/{date}/1min.json"
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