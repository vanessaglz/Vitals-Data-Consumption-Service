from enum import Enum


class ResponseCode(Enum):
    SUCCESS = 0
    ERROR_DUPLICATE_KEY = 1
    ERROR_NOT_FOUND = 2
    ERROR_UNKNOWN = 3
