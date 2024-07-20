import requests
import os
from typing import Dict
import datetime

CURRENT_TOKEN = ""
CURRENT_EXPIRY = -1


class Request:
    def __init__(self, method, url, headers, body=""):
        self.method = method
        self.url = url
        self.headers = headers
        self.body = body

    def __str__(self):
        return f"Request(method={self.method}, url={self.url}, headers={self.headers}, body={self.body})"


class Response:
    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers
        self.body = body

    def __str__(self):
        return (
            f"Response(status={self.status}, headers={self.headers}, body={self.body})"
        )


class CustomHook:

    async def before_request(self, request: Request, **kwargs):
        if request.url.endswith("/oauth/token"):
            return
        client_id = kwargs.get("client_id")
        client_secret = kwargs.environ.get("client_secret")

        if not client_id or not client_secret:
            print("Missing client_id and/or client_secret constructor parameters")
            return

        if not CURRENT_TOKEN or CURRENT_EXPIRY < datetime.datetime.now():
            input_data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
            }

            token_response = await self.doPost(request, input_data, "/oauth2/token")
            expires_in = token_response["data"].get("expires_in")
            access_token = token_response["data"].get("access_token")

            if not expires_in or not access_token:
                print("There is an issue with getting the oauth token")
                return

            CURRENT_EXPIRY = datetime.datetime.now() + expires_in * 1000
            CURRENT_TOKEN = access_token

        authorization = f"Bearer {CURRENT_TOKEN}"
        request.headers.update({"Authorization": authorization})

    def doPost(self, input_data: Dict) -> Dict:
        full_url = f"https://auth.celitech.net/oauth2/token"
        headers = {"Content-type": "application/x-www-form-urlencoded"}

        try:
            resp = requests.post(full_url, data=input_data, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except Exception as error:
            print("Error in posting the request:", error)
            return None

    def after_response(self, request: Request, response: Response, **kwargs):
        pass

    def on_error(
        self, error: Exception, request: Request, response: Response, **kwargs
    ):
        pass
