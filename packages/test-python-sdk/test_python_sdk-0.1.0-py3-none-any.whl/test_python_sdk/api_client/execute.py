import datetime
from typing import Optional

from hexbytes import HexBytes
import requests
from test_python_sdk.api_client.types import ApiClientOpts
from test_python_sdk.api_client.types.eip712order import EIP712OrderAsset, EIP712OrderData, EIP712OrderDomain, EIP712OrderTypes
from test_python_sdk.api_client.types.execute import ExecuteInsertOrder, ExecuteInsertOrderResponse, ExecuteLogin, ExecuteLoginResponse
from test_python_sdk.api_client.types.models import RelayerChain
from test_python_sdk.api_client.types.query import QueryGetLastPricesHistory, QueryGetLastPricesHistoryResponse, QueryGetMarkPricesHistory, QueryGetOrderDepth, QueryGetOrderDepthResponse, QueryGetOrders
from test_python_sdk.utils.exceptions import ExecuteFailedException, QueryFailedException
from test_python_sdk.utils.signed_message_to_str import signed_message_to_str
from test_python_sdk.utils.status_codes import is_successful_status_code
from siwe import SiweMessage
from eth_account.messages import encode_defunct, encode_typed_data
class ExecuteApiClient:
        
    access_token: str
    """
    ExecuteApiClient
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
        
    def login(self):
        message = self._create_siwe(self._opts.chain_id, self._opts.domain)
        signable_message = encode_defunct(text=message)
        signature = self._opts.signer.sign_message(signable_message)
        req = ExecuteLogin(
            message=message,
            signature=signed_message_to_str(signature)
        )
        self._login(req)

    def _login(self, req: ExecuteLogin):
        # Make the POST request with the json parameter
        res = self.session.post(f"{self.url}/api/v1/auth/eth", json=req.dict())

        if not is_successful_status_code(res.status_code):
            raise ExecuteFailedException(f"Failed to login: {res.text}")
        try:
            res = ExecuteLoginResponse(**res.json())
        except Exception:
            raise ExecuteFailedException(res.text)
        self.access_token = res.access_token
        return res
    
    def _create_siwe(self, chain_id: int, domain: Optional[str] = None):
        if (domain is None):
            domain = "perpetuals.volmex.finance"
        origin = "https://perpetuals.volmex.finance"
        statement = "Sign in with Ethereum to the app."
        version = "1"
        nonce = "123456789"
        message = SiweMessage(
            domain=domain, 
            address=self._opts.signer.address, 
            chain_id=chain_id, 
            statement=statement, 
            version=version, 
            nonce=nonce,
            uri=origin,
            issued_at=str(datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds'))
            )
        return message.prepare_message()
        
    def insert_order(self, req: ExecuteInsertOrder, chain: RelayerChain):
        
        if self.access_token is None:
            raise ExecuteFailedException("Access token is not set. ApiClient.login() must be called first.")
        

        res = self.session.post(
            f"{self.url}/api/v1/perpetuals/insertOrder/{chain}", 
            json=req.dict(), 
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        if not is_successful_status_code(res.status_code):
            raise ExecuteFailedException(f"Failed to insert order: {res.text}")
        try:
            res = res.text
        except Exception:
            raise ExecuteFailedException(res.text)
        return res

    def sign_order(self, req: ExecuteInsertOrder, chainId: int, verifyingContract: str):
        domain = EIP712OrderDomain(
            name="V_PERP",
            version="1",
            chainId=chainId,
            verifyingContract=verifyingContract
        )
        types = EIP712OrderTypes(
            Asset=[
                {"name": "virtualToken", "type": "address"},
                {"name": "value", "type": "uint256"}
            ],
            Order=[
                { "name": "orderType", "type": "bytes4" },
                { "name": "deadline", "type": "uint64" },
                { "name": "trader", "type": "address" },
                { "name": "baseAsset", "type": "Asset" },
                { "name": "quoteAsset", "type": "Asset" },
                { "name": "salt", "type": "uint256" },
                { "name": "limitOrderTriggerPrice", "type": "uint128" },
                { "name": "isShort", "type": "bool" },
            ]
            
        )
        
        data = EIP712OrderData(
            orderType=req.order_type,
            deadline=req.deadline,
            trader=req.trader,
            baseAsset=EIP712OrderAsset(value=req.base_asset.value, virtualToken=req.base_asset.virtual_token),
            quoteAsset=EIP712OrderAsset(value=req.quote_asset.value, virtualToken=req.quote_asset.virtual_token),
            salt=req.salt,
            limitOrderTriggerPrice=req.trigger_price,
            isShort=req.is_short
        ) 
        encode_order = encode_typed_data(domain_data=domain.dict(), message_types=types.dict(), message_data=data.dict())
        return self._opts.signer.sign_message(encode_order)
