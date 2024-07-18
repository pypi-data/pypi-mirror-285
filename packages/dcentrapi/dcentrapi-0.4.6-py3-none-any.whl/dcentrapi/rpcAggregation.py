from dcentrapi.Base import Base
from dcentrapi.requests_dappi import requests_get, requests_post


class RpcAggregation(Base):
    def get_token_balance(self, user, token, network, rpc_url=None):
        url = self.url + "tokenBalance"
        data = {"network": network, "user": user, "token": token, "rpc_url": rpc_url}
        response = requests_get(url, params=data, headers=self.headers)
        return response.json()

    def get_token_balances_for_user(self, user, tokens: list, network, rpc_url=None):
        url = self.url + "tokenBalancesForUser"
        data = {"network": network, "user": user, "tokens": tokens, "rpc_url": rpc_url}
        response = requests_post(url, json=data, headers=self.headers)
        return response.json()

    def get_token_balance_for_users(self, users: list, token, network, rpc_url=None):
        url = self.url + "tokenBalanceForUsers"
        data = {"network": network, "users": users, "token": token, "rpc_url": rpc_url}
        response = requests_post(url, json=data, headers=self.headers)
        return response.json()

    def calculate_token_price_from_pair(self, pool, target_token_address, network, rpc_url=None):
        url = self.url + "calculateTokenPriceFromPair"
        data = {"network": network, "lp_token": pool, "target_token_address": target_token_address, "rpc_url": rpc_url}
        response = requests_get(url, params=data, headers=self.headers)
        return response.json()

    def calculate_reserves_amount_from_pair(self, pool, amount, network, rpc_url=None):
        url = self.url + "calculateReservesAmountsFromPair"
        data = {"network": network, "lp_token": pool, "amount": amount, "rpc_url": rpc_url}
        response = requests_get(url, params=data, headers=self.headers)
        return response.json()

    def get_reserves_from_pair(self, pool, network, rpc_url=None):
        url = self.url + "getReservesFromPair"
        data = {"network": network, "lp_token": pool, "rpc_url": rpc_url}
        response = requests_get(url, params=data, headers=self.headers)
        return response.json()

    # Accepted values for factory_type (May 2023):
    # UNI_V2, UNI_V3, CURVE, BALANCER

    def get_reserves_from_pools(self, factory_type, pools: list, network, rpc_url=None):
        url = self.url + "getReservesFromPools"
        data = {
            "factory_type": factory_type,
            "pools": pools,
            "network": network,
            "rpc_url": rpc_url
        }
        response = requests_post(url, json=data, headers=self.headers)
        return response.json()

    # Same accepted factory_type values as for get_reserves_from_pools above
    def get_pool_data_from_factory(self, factory_type, factory, indices: list, network, rpc_url=None):
        url = self.url + "getPoolDataFromFactory"
        data = {
            "factory_type": factory_type,
            "factory": factory,
            "indices": indices,
            "network": network,
            "rpc_url": rpc_url
        }
        response = requests_post(url, json=data, headers=self.headers)
        return response.json()
