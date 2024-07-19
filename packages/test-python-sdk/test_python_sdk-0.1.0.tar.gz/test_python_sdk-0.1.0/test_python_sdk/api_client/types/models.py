
from enum import IntEnum
from typing import Dict, List
from test_python_sdk.utils.enum import StrEnum
from test_python_sdk.utils.model import VolmexBaseModel

class Resolution(StrEnum):
    MINUTE = "1"
    FIVE_MINUTES = "5"
    FIFTEEN_MINUTES = "15"
    THIRTY_MINUTES = "30"
    HOUR = "60"
    DAY = "D"

class RelayerChain(StrEnum):
    VOT = "VOT"
    
class OrderStatus(IntEnum):
    MatchedStatusZero = 1,
    MatchedStatusInit = 2,
    MatchedStatusWaitingForTrigger = 3,
    MatchedStatusValidated = 5,
    MatchedStatusPartialMatchConfirmed = 8,
    MatchedStatusFullMatchConfirmed = 9,
    MatchedStatusSentFailed = 10,
    MatchedStatusBlocked = 11,
    Canceled = 13,
    MatchedStatusPartialMatchPending  = 14,
    MatchedStatusFullMatchPending  = 15,
    MatchStatusCanceledPending = 16,
    

class OrderDepth(VolmexBaseModel):
    """
    Class representing the order depth of a market.
    
    Attributes:
        price (str): The price of the order.
        
        quantity (str): The quantity of the order.
    """
    price: float
    size: str
    
    


class OrderType(StrEnum):
    ORDER = "0xf555eb98"
    STOP_LOSS_INDEX_PRICE = "0x835d5c1e"
    STOP_LOSS_LAST_PRICE = "0xd9ed8042"
    STOP_LOSS_MARK_PRICE = "0xe144c7ec"
    TAKE_PROFIT_INDEX_PRICE = "0x67393efa"
    TAKE_PROFIT_LAST_PRICE = "0xc7dc86f6"
    TAKE_PROFIT_MARK_PRICE = "0xb6d64e04"
    STOP_LOSS_INDEX_PRICE_MARKET = "0x1497a0b3"
    STOP_LOSS_LAST_PRICE_MARKET = "0x3f856051"
    STOP_LOSS_MARK_PRICE_MARKET = "0x390d1f2d"
    TAKE_PROFIT_INDEX_PRICE_MARKET = "0x1fb9dc6e"
    TAKE_PROFIT_LAST_PRICE_MARKET = "0x565085b7"
    TAKE_PROFIT_MARK_PRICE_MARKET = "0x4a11639c"

class OrderStatus(StrEnum):
    MatchedStatusZero = 1
    MatchedStatusInit = 2
    MatchedStatusWaitingForTrigger = 3
    MatchedStatusValidated = 5
    MatchedStatusPartialMatchConfirmed = 8
    MatchedStatusFullMatchConfirmed = 9
    MatchedStatusSentFailed = 10
    MatchedStatusBlocked = 11
    Canceled = 13
    MatchedStatusPartialMatchPending = 14
    MatchedStatusFullMatchPending = 15
    MatchStatusCanceledPending = 16

class Order:
    """
    Class representing an order in a market.
    
    Attributes:
        assets (List[Dict[str, str]]): The assets in the order.
        
        chain_name (str): The chain name of the order.
        
        created_at (int): The timestamp at which the order was created.
        
        deadline (int): The deadline for the order.
        
        fills (str): The fills of the order.
        
        is_short (bool): Whether the order is short.
        
        live_lock_counter (int): The live lock counter of the order.
        
        order_id (str): The ID of the order.
        
        order_type (OrderType): The type of the order.
        
        price (float): The price of the order.
        
        salt (str): The salt of the order.
        
        sign (str): The sign of the order.
        
        status (OrderStatus): The status of the order.
        
        timestamp (str): The timestamp of the order.
        
        trader (str): The trader of the order.
        
        trigger_price (str): The trigger price of the order.
        
        updated_at (int): The timestamp at which the order was updated.
    """
    assets: List[Dict[str, str]]
    chain_name: str
    created_at: int
    deadline: int
    fills: str
    is_short: bool
    live_lock_counter: int
    order_id: str
    order_type: OrderType
    price: float
    salt: str
    sign: str
    status: OrderStatus
    timestamp: str
    trader: str
    trigger_price: str
    updated_at: int
    

class Timeseries:
    """
    Class representing a timeseries.
    
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

#   market: string;
#   minOrderSize: string;
#   virtualToken: string;
#   chain: RelayerChain;
#   fundingPeriod: number;
#   nextFundingTime: number;
#   lastFundingRate: number;
#   baseAsset: string;
#   quoteAsset: string;
#   indexPrice: number;
#   markPrice: number;
#   lastPrice: number;
class Markets:
    """
    Class representing the markets.
    
    Attributes:
        market (str): The market.
        
        min_order_size (str): The minimum order size.
        
        virtual_token (str): The virtual token.
        
        chain (RelayerChain): The chain of the market.
        
        funding_period (int): The funding period of the market.
        
        next_funding_time (int): The next funding time of the market.
        
        last_funding_rate (int): The last funding rate of the market.
        
        base_asset (str): The base asset of the market.
        
        quote_asset (str): The quote asset of the market.
        
        index_price (int): The index price of the market.
        
        mark_price (int): The mark price of the market.
        
        last_price (int): The last price of the market.
    """
    market: str
    min_order_size: str
    virtual_token: str
    chain: RelayerChain
    funding_period: int
    next_funding_time: int
    last_funding_rate: int
    base_asset: str
    quote_asset: str
    index_price: int
    mark_price: int
    last_price: int
    