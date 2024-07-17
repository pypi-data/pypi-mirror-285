import httpx

class UnauthorizedError(Exception):
    pass

class Auths:
    def __init__(self, username, password, host_url=None):
        self.username = username
        self.password = password
        self.host_url = host_url
        if self.host_url is None:
            raise Exception("Host URL is required")
        self.session = httpx.Client()

        response = self.session.post(
            f'{self.host_url}/api/admins/auth-with-password',
            json={
                "identity": self.username,
                "password": self.password
            }
        )
        if response.status_code != 200:
            raise Exception("Login failed")
        self.token = response.json()["token"]

    def get_token(self):
        return self.token
    
    def auth_refresh(self, token=None):
        if token is None:
            raise Exception("Token is required")
        response = self.session.post(
            f'{self.host_url}/api/collections/users/auth-refresh', 
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        if response.status_code != 200:
            raise UnauthorizedError("Token is invalid")
        elif response.status_code == 200:
            return response.json()
        else:
            raise Exception("Failed to refresh token")