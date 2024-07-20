from enum import Enum
from typing import List, Union

import requests

from rumorz.enums import SearchMethod, EntityType, AssetClass, NodeMetrics, Lookback, ScreenerValues


class RumorzClient:
    def __init__(self,
                 api_key,
                 api_url='https://prod-backend-rumorz-l2cw8.ondigitalocean.app'):
        self.api_url = api_url
        self.headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        }
        self._graph = self.Graph(self)
        self._agent = self.Agent(self)

    def _format_data(self, data):
        for key, value in data.items():
            if isinstance(value, Enum):
                data[key] = value.value

    def post(self, endpoint, data):
        url = f"{self.api_url}/{endpoint}"
        self._format_data(data)
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    @property
    def graph(self):
        return self._graph

    @property
    def agent(self):
        return self._agent

    class Graph:
        def __init__(self, api):
            self.api = api

        def get_screener(self,
                         lookback: Union[str, Lookback],
                         screener_values: Union[str, ScreenerValues],
                         entity_type_filter: Union[str, EntityType]):
            params = {
                "lookback": lookback,
                "screener_values": screener_values,
                "entity_type_filter": entity_type_filter
            }
            return self.api.post('graph/screener', params)


    class Agent:
        def __init__(self, api):
            self.api = api

