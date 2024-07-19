from dcentrapi.Base import Base
from dcentrapi.requests_dappi import requests_get


class Web3Index(Base):
    def get_pairs(self, network_name: str, token_address: str):
        url = self.arbitrage_url + "pairs_get" + f"/{network_name}/{token_address}"
        response = requests_get(url, headers=self.headers)
        return response.json()

    def get_factories(self):
        url = self.arbitrage_url + "factories_get"
        response = requests_get(url, headers=self.headers)
        return response.json()
