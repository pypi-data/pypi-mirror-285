import threading
from .deps.auths import Auths
from .db.collection import Collection
import httpx
class PocketBase:
    def __init__(self, host_url, username, password):
        self.host_url = host_url
        self.username = username
        self.password = password

        self.auths = Auths(self.username, self.password, self.host_url)
        self.session = httpx.Client()

    def get_collection(self, collection_name):
        return Collection(self, collection_name)
    
    def get_root_collection(self):
        return Collection(self)
    
    def create_record(self, collection_name, record, token=None, expand: str = "", fields: str = ""):
        collection = self.get_collection(collection_name)
        return collection.create_record(record, token, expand, fields)
    
    def get_all_records(self, collection_name, token=None, page: int = 1, perPage: int = 30, sort: str = "", filter: str = "", expand: str = "", fields: str = "", skipTotal: bool = False):
        collection = self.get_collection(collection_name)
        return collection.get_all_records(token, page, perPage, sort, filter, expand, fields, skipTotal)
    
    def get_record_by_id(self, collection_name, record_id, token=None, expand: str = "", fields: str = ""):
        collection = self.get_collection(collection_name)
        return collection.get_record_by_id(record_id, token, expand, fields)
    
    def update_record(self, collection_name, record_id, record, token=None, expand: str = "", fields: str = ""):
        collection = self.get_collection(collection_name)
        return collection.update_record(record_id, record, token, expand, fields)
    
    def delete_record(self, collection_name, record_id, token=None):
        collection = self.get_collection(collection_name)
        return collection.delete_record(record_id, token)
    
    #Collections
    def create_collection(self, collection, db_type, schema, fields: str = ""):
        return self.get_collection(collection).create_collection(collection, db_type, schema, fields)
    
    def list_collections(self, page: int = 1, perPage: int = 30, sort: str = "", filter: str = "", fields: str = "", skipTotal: bool = False):
        return self.get_root_collection().list_collections(page, perPage, sort, filter, fields, skipTotal)
    
    def get_token(self):
        return self.auths.get_token()
    
    def transaction(self, collection_name):
        def decorator(callback):
            lock = threading.Lock()
            def wrapper(*args, **kwargs):
                with lock:
                    # Acquire the lock before starting the transaction
                    collection = self.get_collection(collection_name)
                    
                    try:
                        # Execute the callback function within the transaction
                        result = callback(collection, *args, **kwargs)
                        
                        # If the callback executed successfully, return the result
                        return result
                    except Exception as e:
                        # If an exception occurs, handle it appropriately
                        # (e.g., retry the operation, log the error, or raise the exception)
                        # You can customize this part based on your specific requirements
                        raise e
            
            return wrapper

        return decorator
    
    def auth_refresh(self, token=None):
        return self.auths.auth_refresh(token)
