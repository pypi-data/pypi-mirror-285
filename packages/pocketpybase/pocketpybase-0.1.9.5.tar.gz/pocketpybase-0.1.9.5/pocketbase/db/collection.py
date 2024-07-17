from ..deps.auths import Auths
import httpx

class Collection:
    def __init__(self, pb, collection_name: str = None):
        self.pb = pb
        self.collection_name = collection_name
        self.auths = Auths(pb.username, pb.password, pb.host_url)
        self.token = self.auths.get_token()
        self.session = httpx.Client()
        
    def status_error(self, response):
        if response.status_code == 400:
            raise Exception("Validation failed")
        elif response.status_code == 403:
            raise Exception("Only admins can create collections")
        elif response.status_code == 404:
            raise Exception("Collection not found")
        elif response.status_code != 200:
            raise Exception("Failed to create collection, status code: " + str(response.status_code)) 
        else:
            return
        
    def create_record(self, record, token=None, expand: str = "", fields: str = ""):
        if token is not None:
            self.token = token
        response = self.session.post(
            f'{self.pb.host_url}/api/collections/{self.collection_name}/records?expand={expand}&fields={fields}',
            json=record,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        self.status_error(response)
        return response.json()
    
    def get_all_records(self, token=None, page: int = 1, perPage: int = 30, sort: str = "", filter: str = "", expand: str = "", fields: str = "", skipTotal: bool = False):
        if token is None:
            token = self.token
        response = self.session.get(
            f'{self.pb.host_url}/api/collections/{self.collection_name}/records?page={page}&perPage={perPage}&sort={sort}&filter={filter}&expand={expand}&fields={fields}&skipTotal={skipTotal}',
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        self.status_error(response)
        return response.json()
    
    def get_record_by_id(self, record_id, token=None, expand: str = "", fields: str = ""):
        if token is not None:
            self.token = token
        response = self.session.get(
            f'{self.pb.host_url}/api/collections/{self.collection_name}/records/{record_id}?expand={expand}&fields={fields}',
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        self.status_error(response)
        return response.json()

    def update_record(self, record_id, record, token=None, expand: str = "", fields: str = ""):
        if token is not None:
            self.token = token
        response = self.session.patch(
            f'{self.pb.host_url}/api/collections/{self.collection_name}/records/{record_id}?expand={expand}&fields={fields}',
            json=record,
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        self.status_error(response)
        return response.json()

    def delete_record(self, record_id, token=None):
        if token is not None:
            self.token = token
        response = self.session.delete(
            f'{self.pb.host_url}/api/collections/{self.collection_name}/records/{record_id}',
            headers={
                "Authorization": f"Bearer {self.token}"
            }
        )
        print(response.status_code)
        if response.status_code != 204:
            raise Exception("Failed to delete record")
        return
    
    #Collections
    def create_collection(self, collection, db_type, schema, fields: str = ""):
        token = self.auths.get_token()
        response = self.session.post(
            f'{self.pb.host_url}/api/collections?fields={fields}',
            json={
                "name": collection,
                "type": db_type,
                "schema": schema
            },
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        self.status_error(response)
        return response.json()
    
    def list_collections(self, page: int = 1, perPage: int = 30, sort: str = "", filter: str = "", fields: str = "", skipTotal: bool = False):
        token = self.auths.get_token()
        response = self.session.get(
            f'{self.pb.host_url}/api/collections?page={page}&perPage={perPage}&sort={sort}&filter={filter}&fields={fields}&skipTotal={skipTotal}',
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        self.status_error(response)
        return response.json()