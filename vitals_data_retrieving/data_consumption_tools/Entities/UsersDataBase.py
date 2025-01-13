from .DataBase import DataBase
from .ResponseCode import ResponseCode
from .CryptoUtils import DataCipher
from .CryptoUtils import hash_data
from dotenv import load_dotenv
import os
import pymongo
import base64


def prepare_data(document_id, token, refresh_token) -> tuple[str, str, str, str]:
    """
    Prepare the data for insertion into the database

    :param document_id: str: Document ID
    :param token: str: Token
    :param refresh_token: str: Refresh token
    :return: tuple[str, str, str, str]: Hashed ID, encoded ID, encoded token, encoded refresh token
    """
    cipher = DataCipher()

    hashed_id = hash_data(document_id)
    ciphered_id = cipher.encrypt(document_id)
    ciphered_token = cipher.encrypt(token)
    ciphered_refresh_token = cipher.encrypt(refresh_token)

    encoded_id = base64.b64encode(ciphered_id).decode('utf-8')
    encoded_token = base64.b64encode(ciphered_token).decode('utf-8')
    encoded_refresh_token = base64.b64encode(ciphered_refresh_token).decode('utf-8')

    return hashed_id, encoded_id, encoded_token, encoded_refresh_token


def decode_data(document) -> dict:
    """
    Decode the data from the database

    :param document: dict: Document
    :return: dict: Decoded document
    """
    cipher = DataCipher()

    encoded_id = base64.b64decode(document.get('user_id'))
    encoded_token = base64.b64decode(document.get('token'))
    encoded_refresh_token = base64.b64decode(document.get('refresh_token'))

    user_id = cipher.decrypt(encoded_id)
    token = cipher.decrypt(encoded_token)
    refresh_token = cipher.decrypt(encoded_refresh_token)

    decoded_document = {
        "user_id": user_id,
        "token": token,
        "refresh_token": refresh_token
    }

    return decoded_document


class UsersDataBase(DataBase):
    def __init__(self):
        if os.path.exists('.env'):
            load_dotenv()
        connection_string = os.environ.get('CONNECTION_STRING')
        database_name = os.environ.get('DATABASE_NAME')
        collection_name = os.environ.get('COLLECTION_NAME')

        client = pymongo.MongoClient(connection_string)
        try:
            client.server_info()
        except pymongo.errors.ServerSelectionTimeoutError:
            raise TimeoutError("Invalid API for MongoDB connection string or timed out when attempting to connect")

        database = client[database_name]
        self.collection = database[collection_name]

    def insert_document(self, document_id, token, refresh_token) -> ResponseCode:
        """
        Insert a document with the specified ID, token, and refresh token

        :param document_id: str: Document ID
        :param token: str: Token
        :param refresh_token: str: Refresh token
        :return: ResponseCode: Response code
        """
        hashed_id, encoded_id, encoded_token, encoded_refresh_token = prepare_data(document_id, token, refresh_token)

        try:
            self.collection.insert_one({
                "_id": hashed_id,
                "user_id": encoded_id,
                "token": encoded_token,
                "refresh_token": encoded_refresh_token
            })
            return ResponseCode.SUCCESS
        except pymongo.errors.DuplicateKeyError:
            return ResponseCode.ERROR_DUPLICATE_KEY
        except Exception as e:
            print(f"Error inserting document: {e}")
            return ResponseCode.ERROR_UNKNOWN

    def read_document(self, document_id) -> tuple[ResponseCode, dict] | tuple[ResponseCode, None]:
        """
        Return the contents of the document containing document_id

        :param document_id: str: Document ID
        :return: tuple[ResponseCode, dict] | tuple[ResponseCode, None]: Response code and document contents
        """
        hashed_id = hash_data(document_id)

        try:
            document = self.collection.find_one({"_id": hashed_id})
            if document:
                return ResponseCode.SUCCESS, document
            else:
                return ResponseCode.ERROR_NOT_FOUND, None
        except Exception as e:
            print(f"Error reading document: {e}")
            return ResponseCode.ERROR_UNKNOWN, None

    def update_document(self, document_id, new_token, new_refresh_token) -> ResponseCode:
        """
        Update the token and refresh token in the document containing document_id

        :param document_id: str: Document ID
        :param new_token: str: New token
        :param new_refresh_token: str: New refresh token
        :return: ResponseCode: Response code
        """
        hashed_id, encoded_id, encoded_token, encoded_refresh_token = (
            prepare_data(document_id, new_token, new_refresh_token))

        try:
            result = self.collection.update_one(
                {"_id": hashed_id},
                {"$set": {"user_id": encoded_id, "token": encoded_token, "refresh_token": encoded_refresh_token}}
            )
            if result.matched_count > 0:
                return ResponseCode.SUCCESS
            else:
                return ResponseCode.ERROR_NOT_FOUND
        except Exception as e:
            print(f"Error updating document: {e}")
            return ResponseCode.ERROR_UNKNOWN

    def delete_document(self, document_id) -> ResponseCode:
        """
        Delete the document containing document_id from the collection

        :param document_id: str: Document ID
        :return: ResponseCode: Response code
        """
        hashed_id = hash_data(document_id)

        try:
            result = self.collection.delete_one({"_id": hashed_id})
            if result.deleted_count > 0:
                return ResponseCode.SUCCESS
            else:
                return ResponseCode.ERROR_NOT_FOUND
        except Exception as e:
            print(f"Error deleting document: {e}")
            return ResponseCode.ERROR_UNKNOWN

    def get_all_documents(self) -> tuple[ResponseCode, list[dict]]:
        """
        Retrieve and return all documents from the collection

        :return: tuple[ResponseCode, list[dict]]: Response code and list of documents
        """
        try:
            documents = list(self.collection.find({}))
            if documents:
                return ResponseCode.SUCCESS, documents
            else:
                return ResponseCode.ERROR_NOT_FOUND, []
        except Exception as e:
            print(f"Error getting all documents: {e}")
            return ResponseCode.ERROR_UNKNOWN, []
