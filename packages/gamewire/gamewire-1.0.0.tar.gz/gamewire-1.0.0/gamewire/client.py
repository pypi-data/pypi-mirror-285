import requests

class GamewireClient:
    BASE_URL = "https://api.gamewire.gg"

    def __init__(self, email, password):
        self.token = None
        self.authenticate(email, password)

    def authenticate(self, email, password):
        response = requests.post(f"{self.BASE_URL}/auth", json={
            "email": email,
            "password": password
        })
        response.raise_for_status()
        data = response.json()
        self.token = data["token"]

    def _make_request(self, method, endpoint, params=None, data=None):
        headers = {"Authorization": f"Bearer {self.token}"}
        url = f"{self.BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()

    def get_balance(self):
        return self._make_request("GET", "/user/balance")

    def get_instance(self):
        return self._make_request("GET", "/instance")

    def start_instance(self):
        return self._make_request("POST", "/instance/start")

    def stop_instance(self):
        return self._make_request("POST", "/instance/stop")

    def get_regions(self):
        return self._make_request("GET", "/instance/regions")

    def get_region(self, region):
        return self._make_request("GET", "/instance/region", params={"region": region})

    def create_instance(self, region, instance_type, os, storage):
        data = {
            "region": region,
            "type": instance_type,
            "os": os,
            "storage": storage
        }
        return self._make_request("POST", "/instance", data=data)

    def delete_instance(self):
        return self._make_request("POST", "/instance/delete")