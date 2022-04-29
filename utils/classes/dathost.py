import os
import requests
from botconfig import requiredEnv


class Dathost:
    def __init__(self):
        self.user = os.getenv(requiredEnv["csgoscrimbot"]["dathost_user"])
        self.auth = os.getenv(requiredEnv["csgoscrimbot"]["dathost_password"])

    def __str__(self):
        return self.user

    async def create_server(self, server_id):
        try:
            with requests.post(f"https://dathost.net/api/0.1/game-servers/{server_id}/duplicate", auth=(self.user, self.auth)) as api_call:
                return api_call
        except requests.exceptions.RequestException as err:
            print(f"Requests error: {err}")
        except requests.exceptions.HTTPError as err:
            print(f"Requests error: {err}")

    def get_servers(self):
        try:
            with requests.get("https://dathost.net/api/0.1/game-servers", auth=(self.user, self.auth)) as api_call:
                return api_call.json()
        except requests.exceptions.RequestException as err:
            print(f"Requests error: {err}")
        except requests.exceptions.HTTPError as err:
            print(f"Requests error: {err}")

    async def start_server(self, server_id):
        try:
            with requests.post(f"https://dathost.net/api/0.1/game-servers/{server_id}/start", auth=(self.user, self.auth)) as api_call:
                return api_call
        except requests.exceptions.RequestException as err:
            print(f"Requests error: {err}")
            return None
        except requests.exceptions.HTTPError as err:
            print(f"Requests error: {err}")
            return None

    async def server_details(self, server_id):
        try:
            with requests.get(f"https://dathost.net/api/0.1/game-servers/{server_id}", auth=(self.user, self.auth)) as api_call:
                return api_call
        except requests.exceptions.RequestException as err:
            print(f"Requests error: {err}")
            return None
        except requests.exceptions.HTTPError as err:
            print(f"Requests error: {err}")
            return None
