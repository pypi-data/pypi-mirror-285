from typing import List, Optional, Union
from test_python_sdk.api_client.types.models import Markets, Order, OrderDepth, RelayerChain, Resolution, Timeseries
from test_python_sdk.utils.model import VolmexBaseModel


class QueryGetOrderDepth(VolmexBaseModel):
    """
    Class representing the query to get the order depth of a perpetual market.
    
    Attributes:
        market (str): The market for which the order depth is to be fetched.
        
        depth (int): The depth of the order book to be fetched.
    """
    token: str
    chain: RelayerChain
    
    
class QueryGetOrderDepthResponse(VolmexBaseModel):
    """
    Class representing the response for the query to get the order depth of a perpetual market.
    
    Attributes:
        asks (List[OrderDepth]): The asks in the order book.
        
        bids (List[OrderDepth]): The bids in the order book.
    """
    ask: List[OrderDepth]
    bid: List[OrderDepth]

class QueryGetOrders(VolmexBaseModel):
    """
    Class representing the query to get the orders of an account in a perpetual market.
    
    Attributes:
        account (str): The account for which the orders are to be fetched.
        
        chain (RelayerChain): The chain on which the orders are to be fetched.
        
        first (Optional[int]): The number of orders to fetch.
        
        skip (Optional[int]): The number of orders to skip.
        
        filter_status (Optional[List[int]]): The status of the orders to filter by.
    """
    account: str
    chain: RelayerChain
    first: Optional[int]
    skip: Optional[int]
    filter_status: Optional[List[int]]

class OrderAsset(VolmexBaseModel):
    id: int
    orderbook_id: str
    virtual_token: str
    value: str
    
class QueryGetOrder(VolmexBaseModel):
    order_id: str
    order_type: str
    trader: str
    deadline: int
    is_short: bool
    Assets: List[OrderAsset]
    status: int
    price: int
    salt: str
    trigger_price: str
    sign: str
    live_lock_counter: int
    fills: str
    timestamp: str
    created_at: int
    updated_at: int
    chain_name: str


class QueryGetOrdersResponse(VolmexBaseModel):
    """
    Class representing the response for the query to get the orders of an account in a perpetual market.
    
    Attributes:
        orders (List[Order]): The orders of the account.
    """
    orders: List[QueryGetOrder]

class QueryGetLastPricesHistory(VolmexBaseModel):
    """
    Class representing the query to get the last prices history of a perpetual market.
    
    Attributes:
        token (str): The token for which the last prices history is to be fetched.
        
        chain (RelayerChain): The chain on which the last prices history is to be fetched.
        
        resolution (Resolution): The resolution of the last prices history.
        
        from_timestamp (int): The start timestamp of the last prices history.
        
        to_timestamp (int): The end timestamp of the last prices history.
    """
    token: str
    chain: RelayerChain
    resolution: Resolution
    from_timestamp: int
    to_timestamp: int
    
class QueryGetLastPricesHistoryResponse(VolmexBaseModel):
    """
    Class representing the response for the query to get the last prices history of a perpetual market.
    Attributes:
        c (List[float]): The close values of the timeseries.
        
        h (List[float]): The high values of the timeseries.
        
        l (List[float]): The low values of the timeseries.
        
        o (List[float]): The open values of the timeseries.
        
        t (List[float]): The timestamps of the timeseries.
        
        s (str): The status of the timeseries.
    """
    c: List[float]
    h: List[float]
    l: List[float]
    o: List[float]
    t: List[float]
    s: str
    
    
class QueryGetMarkPricesHistory(VolmexBaseModel):
    """
    Class representing the query to get the mark prices history of a perpetual market.
    
    Attributes:
        token (str): The token for which the mark prices history is to be fetched.
        
        chain (RelayerChain): The chain on which the mark prices history is to be fetched.
        
        resolution (Resolution): The resolution of the mark prices history.
        
        from_timestamp (int): The start timestamp of the mark prices history.
        
        to_timestamp (int): The end timestamp of the mark prices history.
    """
    token: str
    chain: RelayerChain
    resolution: Resolution
    from_timestamp: int
    to_timestamp: int
    
class QueryGetMarkPricesHistoryResponse(VolmexBaseModel):
    """
    Class representing the response for the query to get the mark prices history of a perpetual market.
    Attributes:
        c (List[float]): The close values of the timeseries.
        
        h (List[float]): The high values of the timeseries.
        
        l (List[float]): The low values of the timeseries.
        
        o (List[float]): The open values of the timeseries.
        
        t (List[float]): The timestamps of the timeseries.
        
        s (str): The status of the timeseries.
    """
    c: List[float]
    h: List[float]
    l: List[float]
    o: List[float]
    t: List[float]
    s: str
    
class QueryGetMarkets(VolmexBaseModel):
    """
    Class representing the query to get the markets of a token on a chain.
    
    Attributes:
        token (str): The token for which the markets are to be fetched.
        
        chain (RelayerChain): The chain on which the markets are to be fetched.
    """
    token: str
    chain: RelayerChain
    
class QueryGetMarketsResponse(VolmexBaseModel):
    """
    Class representing the response for the query to get the markets of a token on a chain.
    
    Attributes:
        markets (List[str]): The markets of the token.
    """
    markets: List[Markets]
    
# # TODO: check
# class QueryGetStreamingDepth(VolmexBaseModel):
#     """
#     Class representing the query to get the streaming depth of a perpetual market.
    
#     Attributes:
#         token (str): The token for which the streaming depth is to be fetched.
        
#         chain (RelayerChain): The chain on which the streaming depth is to be fetched.
        
#         on_ping (StreamOnPingFn): The function to be called on ping.
        
#         on_message (StreamOnMessageFn[StreamingDepthMessage]): The function to be called on message.
#     """
#     token: str
#     chain: RelayerChain
#     on_ping: StreamOnPingFn
#     on_message: StreamOnMessageFn[StreamingDepthMessage]

# class QueryGetStreamingMarkets(VolmexBaseModel):
#     """
#     Class representing the query to get the streaming markets of a token on a chain.
    
#     Attributes:
#         token (str): The token for which the streaming markets are to be fetched.
        
#         chain (RelayerChain): The chain on which the streaming markets are to be fetched.
        
#         on_ping (StreamOnPingFn): The function to be called on ping.
        
#         on_message (StreamOnMessageFn[StreamingMarketsMessage]): The function to be called on message.
#     """
#     token: str
#     chain: RelayerChain
#     on_ping: StreamOnPingFn
#     on_message: StreamOnMessageFn[StreamingMarketsMessage]