
from typing import List
from test_python_sdk.utils.model import VolmexBaseModel

class EIP712OrderDomain(VolmexBaseModel):
    name: str
    version: str
    chainId: int
    verifyingContract: str
    
class EIP712OrderTypesSection(VolmexBaseModel):
    name: str
    type: str
class EIP712OrderTypes(VolmexBaseModel):
    Asset: List[EIP712OrderTypesSection]
    Order: List[EIP712OrderTypesSection]

class EIP712OrderAsset(VolmexBaseModel):
    """
    Class representing the query to insert an asset into an order.
    
    Attributes:
        virtualToken (str): The virtual token of the asset to be inserted.
        
        value (str): The value of the asset to be inserted.
    """
    virtualToken: str
    value: str
class EIP712OrderData(VolmexBaseModel):
    """
    Class representing the query to insert an order into a perpetual market.
    
    Attributes:
        orderType (str): The type of the order to be inserted.
        
        deadline (str): The deadline for the order to be inserted.
        
        trader (str): The trader who is inserting the order.
        
        baseAsset (EIP712OrderAsset): The base asset of the order.
        
        quoteAsset (EIP712OrderAsset): The quote asset of the order.
        
        salt (str): The salt for the order to be inserted.
        
        limitOrderTriggerPrice (str): The trigger price for the order to be inserted.
        
        isShort (bool): Whether the order is a short order.
    """
    orderType: str
    deadline: str
    trader: str
    baseAsset: EIP712OrderAsset
    quoteAsset: EIP712OrderAsset
    salt: str
    limitOrderTriggerPrice: str
    isShort: bool