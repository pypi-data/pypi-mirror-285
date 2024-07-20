# task_manager.py
import logging
from sws_api_client.sws_api_client import SwsApiClient
logger = logging.getLogger(__name__)

class Tags:

    def __init__(self, sws_client: SwsApiClient, endpoint: str = 'tag_api') -> None:
        self.sws_client = sws_client
        self.endpoint = endpoint

    def get_read_access_url(self, path: str, expiration: int) -> dict:

        url = f"/tags/dissemination/getReadAccessUrl"
        body = {"path": path, "expiration": expiration}

        response = self.sws_client.discoverable.post(self.endpoint, url, data=body)

        return response
