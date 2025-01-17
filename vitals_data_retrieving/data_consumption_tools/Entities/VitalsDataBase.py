from .DataBase import DataBase
from .ResponseCode import ResponseCode
from dotenv import load_dotenv
import os
import pymongo


class VitalsDataBase(DataBase):
    def __init__(self):
        if os.path.exists('.env'):
            load_dotenv()
        connection_string = os.environ.get('CONNECTION_STRING')
        database_name = os.environ.get('DATABASE_NAME')
        collection_name = os.environ.get('VITALS_COLLECTION')

        client = pymongo.MongoClient(connection_string)
        try:
            client.server_info()
        except pymongo.errors.ServerSelectionTimeoutError:
            raise TimeoutError("Invalid API for MongoDB connection string or timed out when attempting to connect")

        database = client[database_name]
        self.collection = database[collection_name]

    def insert_document(self, user_id, date, data) -> ResponseCode:
        """
        Insert a document with the specified ID, token, and refresh token

        :param user_id: str: User ID (hashed)
        :param date: str: Date
        :param data: dict: Data in JSON format
        :return: ResponseCode: Response code
        """
        try:
            self.collection.insert_one({
                "user_id": user_id,
                "date": date,
                "data": data
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

        :param document_id: str: Document ID (hashed User ID)
        :return: tuple[ResponseCode, dict] | tuple[ResponseCode, None]: Response code and document contents
        """
        try:
            document = self.collection.find_one({"_id": document_id})
            if document:
                return ResponseCode.SUCCESS, document
            else:
                return ResponseCode.ERROR_NOT_FOUND, None
        except Exception as e:
            print(f"Error reading document: {e}")
            return ResponseCode.ERROR_UNKNOWN, None

    def update_document(self, document_id, new_token, new_refresh_token) -> ResponseCode:
        # Method not implemented
        pass

    def delete_document(self, document_id) -> ResponseCode:
        """
        Delete the document containing document_id from the collection

        :param document_id: str: Document ID
        :return: ResponseCode: Response code
        """
        try:
            result = self.collection.delete_one({"_id": document_id})
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
