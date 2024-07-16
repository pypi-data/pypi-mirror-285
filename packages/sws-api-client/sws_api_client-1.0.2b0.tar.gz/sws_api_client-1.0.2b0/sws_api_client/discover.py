import logging
import os
import requests

from sws_api_client.token import Token

logger = logging.getLogger(__name__)

class Discover:

    def __init__(self,sws_endpoint:str,sws_token:str, token:Token) -> None:
        self.sws_endpoint = sws_endpoint
        self.sws_token = sws_token
        self.token = token
        self.discover = self.__get_discover()
        logger.debug(f"Discover initialized with endpoint {sws_endpoint} and token {sws_token}")

    def __get_discover(self) -> dict:
        token = self.token.get_token()
        discover_endpoint = f"{self.sws_endpoint}/discover"
        headers = {"Authorization": token.access_token, 'sws-token': self.sws_token}
        
        return requests.get(url=discover_endpoint, headers=headers).json()
    
    def call(self, method: str, endpoint: str, path: str, params: dict = None, headers: dict = None, data: dict = None) -> dict:
        if not endpoint:
            raise ValueError("An endpoint must be provided.")

        if endpoint not in self.discover or 'path' not in self.discover[endpoint]:
            raise ValueError(f"endpoint '{endpoint}' not found")
        
        x_api_key = self.discover[endpoint].get("key", "")
        full_path = f"{self.discover[endpoint]['path']}{path}"
        token = self.token.get_token()
        full_headers = {"Authorization": token.access_token, "sws-token": self.sws_token}
        if x_api_key:
            full_headers["x-api-key"] = x_api_key

        if headers:
            full_headers.update(headers)

        request_func = getattr(requests, method.lower())
        response = request_func(full_path, params=params, headers=full_headers, json=data)

        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as errh:
            logger.error(f"HTTP Error: {errh}")
            logger.error(f"HTTP Status Code: {errh.response.status_code}")
            logger.error(f"Response Text: {errh.response.text}")
            logger.error(f"Request URL: {errh.request.url}")
        except requests.exceptions.RequestException as err:
            logger.error(f"Request Exception: {err}")

        return {}

    def get(self, endpoint, path: str, params: dict = None, headers: dict = None) -> dict:
        return self.call("GET", endpoint, path, params=params, headers=headers)

    def post(self, endpoint, path: str, data: dict = None, params: dict = None, headers: dict = None) -> dict:
        return self.call("POST", endpoint, path, params=params, headers=headers, data=data)

    def put(self, endpoint, path: str, data: dict = None, params: dict = None, headers: dict = None) -> dict:
        return self.call("PUT", endpoint, path, params=params, headers=headers, data=data)

    def delete(self, endpoint, path: str, params: dict = None, headers: dict = None) -> dict:
        return self.call("DELETE", endpoint, path, params=params, headers=headers)
