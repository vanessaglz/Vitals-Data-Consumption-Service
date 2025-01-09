from .ResponseCode import ResponseCode
from abc import ABCMeta, abstractmethod
from typing import Tuple


class DataBase(metaclass=ABCMeta):

    @abstractmethod
    def insert_document(self, document_id, token, refresh_token) -> ResponseCode:
        """
        Insert a document with the specified ID, token, and refresh token

        :param document_id: str: Document ID
        :param token: str: Token
        :param refresh_token: str: Refresh token
        :return: ResponseCode: Response code
        """
        pass

    @abstractmethod
    def read_document(self, document_id) -> Tuple[ResponseCode, dict] | Tuple[ResponseCode, None]:
        """
        Return the contents of the document containing document_id

        :param document_id: str: Document ID
        :return: Tuple[ResponseCode, dict] | Tuple[ResponseCode, None]: Response code and document contents
        """
        pass

    @abstractmethod
    def update_document(self, document_id, new_token, new_refresh_token) -> ResponseCode:
        """
        Update the token and refresh token in the document containing document_id

        :param document_id: str: Document ID
        :param new_token: str: New token
        :param new_refresh_token: str: New refresh token
        :return: ResponseCode: Response code
        """
        pass

    @abstractmethod
    def delete_document(self, document_id) -> ResponseCode:
        """
        Delete the document containing document_id from the collection

        :param document_id: str: Document ID
        :return: ResponseCode: Response code
        """
        pass

    @abstractmethod
    def get_all_documents(self) -> Tuple[ResponseCode, list[dict]]:
        """
        Retrieve and return all documents from the collection

        :return: Tuple[ResponseCode, list[dict]]: Response code and list of documents
        """
        pass
