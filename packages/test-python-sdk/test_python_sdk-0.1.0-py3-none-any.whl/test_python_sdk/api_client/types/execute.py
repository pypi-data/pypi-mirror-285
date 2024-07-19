from typing import List, Optional
from test_python_sdk.api_client.types.query import QueryGetOrder
from test_python_sdk.utils.model import VolmexBaseModel

class ExecuteInsertOrderAsset(VolmexBaseModel):
    """
    Class representing the query to insert an asset into an order.
    
    Attributes:
        virtual_token (str): The virtual token of the asset to be inserted.
        
        value (str): The value of the asset to be inserted.
    """
    virtual_token: str
    value: str

class ExecuteInsertOrder(VolmexBaseModel):
    """
    Class representing the query to insert an order into a perpetual market.
    
    Attributes:
        order_type (str): The type of the order to be inserted.
        
        deadline (str): The deadline for the order to be inserted.
        
        trader (str): The trader who is inserting the order.
        
        base_asset (ExecuteInsertOrderAsset): The base asset of the order.
        
        quote_asset (ExecuteInsertOrderAsset): The quote asset of the order.
        
        salt (str): The salt for the order to be inserted.
        
        trigger_price (str): The trigger price for the order to be inserted.
        
        is_short (bool): Whether the order is a short order.
        
        signature (str): The signature for the order to be inserted.
    """
    order_type: str
    deadline: str
    trader: str
    base_asset: ExecuteInsertOrderAsset
    quote_asset: ExecuteInsertOrderAsset
    salt: str
    trigger_price: str
    is_short: bool
    signature: Optional[str]


ExecuteInsertOrderResponse = str
    
    
class ExecuteLogin(VolmexBaseModel):
    """
    Class representing the query to login into the API.
    
    Attributes:
        signature (str): The signature for the login request.
        
        message (str): The message for the login request.
    """
    signature: str
    message: str
    
class ExecuteLoginResponse(VolmexBaseModel):
    """
    Class representing the response for the query to login into the API.
    
    Attributes:
        access_token (str): The token for the logged in user.
    """
    access_token: str
    
    
class ExecuteCancelOrder(QueryGetOrder):
    pass