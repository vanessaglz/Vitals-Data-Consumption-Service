from enum import Enum


class DataScopeEnum(Enum):
    """
    Enum class for the data scope of the wearable devices
    """
    user_info = 'get_user_info'
    sleep = 'get_sleep_data'
    heart_rate = 'get_heart_rate_data'
    spO2 = 'get_spO2_data'
    heart_rate_variability = 'get_heart_rate_variability_data'
    heart_rate_intraday = 'get_heart_rate_intraday_data'
