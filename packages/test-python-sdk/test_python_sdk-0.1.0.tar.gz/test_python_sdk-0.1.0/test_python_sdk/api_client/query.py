import requests
from test_python_sdk.api_client.types import ApiClientOpts
from test_python_sdk.api_client.types.query import QueryGetLastPricesHistory, QueryGetLastPricesHistoryResponse, QueryGetMarkPricesHistory, QueryGetOrder, QueryGetOrderDepth, QueryGetOrderDepthResponse, QueryGetOrders, QueryGetOrdersResponse
from test_python_sdk.utils.exceptions import QueryFailedException
from test_python_sdk.utils.status_codes import is_successful_status_code

class QueryApiClient:
    """
    Client class for querying the off-chain engine.
    """
    
    def __init__(self, opts: ApiClientOpts):
        """
        Initializes the client with the given options.
        
        Args:
            opts (ApiClientOpts): The options for the client.
        """
        self._opts : ApiClientOpts = ApiClientOpts.parse_obj(opts)
        self.url: str = self._opts.url
        self.session = requests.Session()
    
    def get_order_depth(self, req: QueryGetOrderDepth):
        res = self.session.get(f"{self.url}/api/v1/perpetuals/depth/{req.token}/{req.chain}")
        if not is_successful_status_code(res.status_code):
            raise Exception(f"Failed to get order depth: {res.text}")
        try:
            query_res = QueryGetOrderDepthResponse(**res.json())
        except Exception:
            raise QueryFailedException(res.text)
        return query_res
    
    def get_orders(self, req: QueryGetOrders):
        if req.filter_status is None:
            req.filter_status = []
        res = self.session.get(f"{self.url}/api/v1/perpetuals/getOrders/{req.account}/{req.chain}?first={req.first}&skip={req.skip}&filterByStatus={','.join(map(str, req.filter_status))}")
        if not is_successful_status_code(res.status_code):
            raise Exception(f"Failed to get orders: {res.text}")
        try:
            orders = [QueryGetOrder(**order) for order in res.json()]
            query_res = QueryGetOrdersResponse(
                orders=orders
            )
        except Exception:
            raise QueryFailedException(res.text)
        return query_res
    

    def get_last_prices_history(self, req: QueryGetLastPricesHistory):
        res = self.session.get(f"{self.url}/api/v1/perpetuals/last_prices_history/{req.chain}/{req.token}?resolution={req.resolution}&from={req.from_timestamp}&to={req.to_timestamp}")
        if not is_successful_status_code(res.status_code):
            raise Exception(f"Failed to get last prices history: {res.text}")
        try:
            query_res = QueryGetLastPricesHistoryResponse(**res.json())
        except Exception:
            raise QueryFailedException(res.text)
        return query_res
    
    def get_mark_prices_history(self, req: QueryGetMarkPricesHistory):
        res = self.session.get(f"{self.url}/api/v1/perpetuals/mark_prices_history/{req.chain}/{req.token}?resolution={req.resolution}&from={req.from_timestamp}&to={req.to_timestamp}")
        if not is_successful_status_code(res.status_code):
            raise Exception(f"Failed to get mark prices history: {res.text}")
        try:
            query_res = QueryGetLastPricesHistoryResponse(**res.json())
        except Exception:
            raise QueryFailedException(res.text)
        return query_res
    
    # TODO : streaming depth, streaming markets, insert order
    
    
