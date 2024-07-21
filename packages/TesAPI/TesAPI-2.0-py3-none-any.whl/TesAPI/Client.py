import json

import requests.exceptions
from requests import post, get, options, put
from .Exceptions import SettingError, RequestError, RSAIsNone
from TesRSA import Key, Crypt

rsa = None


class Client:
    def __init__(self, username: str | None = None, token: str | None = None):
        if (len(username) == 0 and type(username) != None) or (len(token) == 0 and type(token) != None):
            raise SettingError("The length of the username and token must not be zero")
        self.username, self.token = username, token
        self.endpoint = "http://127.0.0.1:8000" #http://tesapi.ddns.net
        self.AI_Request = self._AI_Request_Class(self)
        self.Information = self._Information_Class(self)
        self.rsa = self._rsa(self)


    class _rsa:
        def __init__(self, data):
            self.data = data

        def get(self):
            try:
                global rsa
                req = get(f"{self.data.endpoint}/api/rsa")
                rsa = Key.load_public_key(req.text.encode())
            except ConnectionError:
                raise RequestError("Error while connect to TesAPI")


    class _AI_Request_Class:
        def __init__(self, data):
            self.data = data

        def chat(self, message, model):
            try:
                if rsa is None:
                    raise RSAIsNone("RSA Is None, get RSA from TesAPI `/api/rsa` to fix")
                body = {
                    "auth": {
                        "username": self.data.username,
                        "token": self.data.token
                    },
                    "detail": {
                        "message": message
                    }
                }
                ciphertext = Crypt.encrypt_content(content=json.dumps(body), public_key=rsa)

                resp = http.request(
                    uri= self.data.endpoint + f"/api/ai/chat/{model}",
                    body=ciphertext,
                    method="post"
                )
            except ConnectionError:
                raise RequestError("ERROR While Connect to TesAPI")
            return resp


    class _Information_Class:
        def __init__(self, data):
            self.data = data

        def models(self):
            try:
                resp = http.request(
                    uri=self.data.endpoint + "/api/ai/models",
                    body={},
                    method="get"
                )
            except requests.exceptions.ConnectionError:
                raise RequestError("ERROR While Connect to TesAPI")

            return resp


class http:
    routes = {
        "post": post,
        "get": get,
        "put": put,
        "options": options
    }

    @staticmethod
    def request(*, uri: str, body: dict | bytes, method: str):
        if type(body) is dict:
            response = http.routes[method](
                url=uri,
                json=body
            )
        else:
            response = http.routes[method](
                url=uri,
                data=body
            )
        return response.json()