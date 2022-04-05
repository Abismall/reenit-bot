import os
from dotenv import load_dotenv
import requests
from botconfig import requiredEnv


class Dathost:
    def __init__(self):
        self.user = os.getenv(requiredEnv["csgoscrimbot"]["dathost_user"])
        self.auth = os.getenv(requiredEnv["csgoscrimbot"]["dathost_password"])

    def __str__(self):
        return self.user

    def create_server(self, server_id):
        try:
            return requests.post(f"https://dathost.net/api/0.1/game-servers/{server_id}/duplicate", auth=(self.user, self.auth))
        except requests.exceptions.RequestException as err:
            print(f"Requests error: {err}")
        except requests.exceptions.HTTPError as err:
            print(f"Requests error: {err}")

    def start_server(self, server_id):
        try:
            return requests.post(f"https://dathost.net/api/0.1/game-servers/{server_id}/start", auth=(self.user, self.auth))
        except requests.exceptions.RequestException as err:
            print(f"Requests error: {err}")
            return None
        except requests.exceptions.HTTPError as err:
            print(f"Requests error: {err}")
            return None

    async def server_details(self, server_id):
        try:
            return requests.get(f"https://dathost.net/api/0.1/game-servers/{server_id}", auth=(self.user, self.auth))
        except requests.exceptions.RequestException as err:
            print(f"Requests error: {err}")
            return None
        except requests.exceptions.HTTPError as err:
            print(f"Requests error: {err}")
            return None
