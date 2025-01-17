from enum import Enum


class DataEndpointsEnum(Enum):
    """
    Enum class for the Fitbit API endpoints.
    """
    # Get user info from the wearable device API.
    user_info = "https://api.fitbit.com/1/user/-/devices.json"

    # Get user's sleep log entries for a given date. The detail level includes duration (minutes), efficiency,
    # and minutes of the sleep stages (deep, light, rem, wake).
    sleep = "https://api.fitbit.com/1.2/user/-/sleep/date/{date}.json"

    # Get heart rate data by second for a specific date from the wearable device API.
    heart_rate = "https://api.fitbit.com/1/user/-/activities/heart/date/{date}/1d/1sec.json"

    # Get heart rate variability data for a specific second from the wearable device API.
    heart_rate_variability = "https://api.fitbit.com/1/user/-/hrv/date/{date}/all.json"

    # Get respiratory rate intraday data for a specific date. Calculates average respiratory rate and
    # classifies rates by sleep stages.
    breathing_rate = "https://api.fitbit.com/1/user/-/br/date/{date}/all.json"

    # Get intraday SpO2 (oxygen saturation) data for a specific date. Calculates average SpO2 and provides
    # detailed data at 1-second intervals.
    spO2 = "https://api.fitbit.com/1/user/-/spo2/date/{date}/all.json"

    # Get intraday activity time series data (steps) for a specific date. Provides detailed step counts at
    # 1-minute intervals.
    activity = "https://api.fitbit.com/1/user/-/activities/steps/date/{date}/1d/1min.json"
