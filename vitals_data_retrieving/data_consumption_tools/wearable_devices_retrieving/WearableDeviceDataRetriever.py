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
    def retrieve_data(self) -> str:
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
