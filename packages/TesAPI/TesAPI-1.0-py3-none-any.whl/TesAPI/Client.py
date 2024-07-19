import requests.exceptions
from requests import post, get, options, put
from .Exceptions import SettingError, RequestError


class Client:
    def __init__(self, username: str | None = None, token: str | None = None):
        if (len(username) == 0 and type(username) != None) or (len(token) == 0 and type(token) != None):
            raise SettingError("The length of the username and token must not be zero")
        self.username, self.token = username, token
        self.endpoint = "http://tesapi.ddns.net:22544"
        self.AI_Request = self._AI_Request_Class(self)
        self.Information = self._Information_Class(self)



    class _AI_Request_Class:
        def __init__(self, data):
            self.data = data

        def chat(self, message, model):
            try:
                resp = http.request(
                    uri= self.data.endpoint + f"/api/ai/chat/{model}",
                    headers={
                        "username": self.data.username,
                        "token": self.data.token
                    },
                    body={
                        "detail": {
                            "message": message
                        }
                    },
                    method="post"
                )
            except requests.exceptions.ConnectionError:
                raise RequestError("ERROR While Connect to TesAPI")

            return resp


    class _Information_Class:
        def __init__(self, data):
            self.data = data

        def models(self):
            try:
                resp = http.request(
                    uri=self.data.endpoint + "/api/ai/models",
                    headers={},
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
    def request(*, uri: str, headers: dict, body: dict, method: str):
        response = http.routes[method](
            url=uri,
            headers=headers,
            json=body
        )
        return response.json()