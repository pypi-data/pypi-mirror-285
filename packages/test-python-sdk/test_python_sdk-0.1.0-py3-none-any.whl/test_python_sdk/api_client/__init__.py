from test_python_sdk.api_client.execute import ExecuteApiClient
from test_python_sdk.api_client.query import QueryApiClient
from test_python_sdk.api_client.types import ApiClientOpts


class ApiClient(QueryApiClient, ExecuteApiClient):
    """
    Client for interacting with the perps api.
    """
    
    chain_id: int
    
    def __init__(self, opts: ApiClientOpts):
        self.chain_id = opts.chain_id
        QueryApiClient.__init__(self, opts)
        ExecuteApiClient.__init__(self, opts)