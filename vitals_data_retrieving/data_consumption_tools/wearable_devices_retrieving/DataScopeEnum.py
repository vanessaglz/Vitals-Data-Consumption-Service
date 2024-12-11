from enum import Enum


class DataScopeEnum(Enum):
    """
    Enum class for the data scope of the wearable devices
    """
    user_info = 'get_user_info'
    sleep = 'get_sleep_data'
    heart_rate = 'get_heart_rate_data'
    heart_rate_variability = 'get_heart_rate_variability_data'
    breathing_rate = 'get_breathing_rate_data'
    spO2 = 'get_oxygen_saturation_data'
    activity = 'get_activity_data'
