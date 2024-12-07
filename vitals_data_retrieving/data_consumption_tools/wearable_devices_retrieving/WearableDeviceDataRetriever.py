from abc import ABCMeta, abstractmethod


class WearableDeviceDataRetriever(metaclass=ABCMeta):

    @abstractmethod
    def connect_to_api(self) -> str:
        """
        Connect to the API of the wearable device
        :arg: None
        :return: str: Authorization string
        """
        pass

    @abstractmethod
    def get_user_info(self, token) -> str:
        """
        Get user info from the wearable device API
        :arg: None
        :return: str: User info
        """
        pass

    @abstractmethod
    def retrieve_data(
            self, token: str = None, start_date: str = None, end_date: str = None, scope: list[str] = None) -> str:
        """
        Retrieve data from the wearable device by querying the API
        :arg: None
        :return: str: Data
        """
        pass

    @abstractmethod
    def get_authorization_token(self, authorization_response) -> str:
        """
        Get the authorization token from the API
        :param authorization_response: str: URL
        :return: str: Authorization token
        """
        pass
