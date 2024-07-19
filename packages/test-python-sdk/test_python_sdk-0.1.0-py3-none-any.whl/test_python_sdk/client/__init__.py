from datetime import datetime
import calendar
from decimal import Decimal
from typing import Optional
from test_python_sdk.api_client.types.query import QueryGetOrders
from test_python_sdk.utils.order import get_open_order_statuses
from web3.contract.contract import ContractFunction
from test_python_sdk.api_client.types.models import OrderType, RelayerChain
from test_python_sdk.utils.signed_message_to_str import signed_message_to_str
from web3 import Web3
from test_python_sdk.api_client import ApiClient
from test_python_sdk.api_client.types import ApiClientOpts, Signer
from test_python_sdk.api_client.types.execute import ExecuteCancelOrder, ExecuteInsertOrder, ExecuteInsertOrderAsset
from test_python_sdk.client.context import VolmexClientContext, VolmexClientContextOpts
from test_python_sdk.contracts import VolmexContracts, VolmexContractsContext
from test_python_sdk.contracts.loader import load_deployment
from test_python_sdk.contracts.types import VolmexDeployment, VolmexDeploymentBaseTokens, VolmexDeploymentCollateral, VolmexDeploymentContracts, VolmexNetwork
from test_python_sdk.utils.model import VolmexBaseModel


class VolmexClient:
    """
    This is the main class for interacting with the Volmex Perpetuals DEX V1.
    
    Note:
        Use `create_volmex_client` for creating instances.
    """
    
    context: VolmexClientContext
    api: ApiClient
    contracts: VolmexContracts
    deployment: VolmexDeployment
    deployment_contracts: VolmexDeploymentContracts
    deployment_collateral: VolmexDeploymentCollateral
    deployment_base_token: VolmexDeploymentBaseTokens
    prev_salt: int = 0

    def __init__(self, context: VolmexClientContext):
        self.context = context
        self.api = context.api_client
        self.contracts = context.contracts
        self.deployment = context.deployment
        self.deployment_base_token = context.base_tokens
        self.deployment_collateral = context.collateral
        self.deployment_contracts = context.contracts
    
    def login(self):
        """
            Login to access certain endpoints on the API.
        """
        return self.api.login()
    
    def get_open_orders(self, chain: str, first: int, skip: int):
        return self.api.get_orders(QueryGetOrders(
            chain=chain,
            first=first,
            skip=skip,
            filter_status=get_open_order_statuses()
        ))
    
    def cancel_order(self, req: ExecuteCancelOrder):
        params = {
            'baseAsset': {
                'virtualToken': req.Assets[0].virtual_token,
                'value': int(req.Assets[0].value),
            },
            'quoteAsset': {
                'virtualToken': req.Assets[1].virtual_token,
                'value': int(req.Assets[1].value),
            },
            'deadline': int(req.deadline),
            'isShort': req.is_short,
            'limitOrderTriggerPrice': int(req.trigger_price),
            'orderType': str(req.order_type),
            'salt': int(req.salt),
            'trader': req.trader,
        }
        func = self.contracts.matching_engine.functions.cancelOrder(
            (
                params['orderType'],
                params['deadline'],
                params['trader'],
                    (
                        params['baseAsset']['virtualToken'],
                        params['baseAsset']['value']
                    ),
                    (
                        params['quoteAsset']['virtualToken'],
                        params['quoteAsset']['value']
                    ),
                params['salt'],
                params['limitOrderTriggerPrice'],
                params['isShort']
            )
        )
        return self.execute_tx(func)
    
    def cancel_all_orders(self):
        orders_res = self.get_open_orders(
            account=self.context.signer.address,
            chain=RelayerChain.VOT.value,
            first=1,
            skip=0
        )
        if (len(orders_res.orders) == 0):
            print("No orders to cancel")
            return None
        func = self.contracts.matching_engine.functions.cancelAllOrders(int(orders_res.orders[0].salt) + 1)
        return self.execute_tx(func)
    
    def allowance_periphery(self, token_addr: str):
        return self.allowance(token_addr, self.contracts.periphery.address)
    
    def allowance(self, token_addr: str, spender_addr: str):
        return self.contracts.factory.erc20(token_addr).functions.allowance(self.context.signer.address, spender_addr).call()
    
    def approve_periphery(self, token_addr: str, amount: str):
        return self.approve(token_addr, self.contracts.periphery.address, amount)
    
    def approve(self, token_addr: str, spender_addr: str, amount: str):
        func = self.contracts.factory.erc20(token_addr).functions.approve(spender_addr, int(amount))
        return self.execute_tx(func)
    
    def deposit(self, amount: str, collateral_addr: str):
        func = self.contracts.periphery.functions.depositToVault(0, collateral_addr, int(amount), self.context.signer.address)
        return self.execute_tx(func)
    
    def withdraw(self, amount: str, collateral_addr: str):
        func = self.contracts.periphery.functions.withdrawFromVault(0, collateral_addr, int(amount))
        return self.execute_tx(func)
    
    def execute_tx(self, func: ContractFunction):
        nonce = self.contracts.w3.eth.get_transaction_count(self.context.signer.address)
        tx_params = func.build_transaction({
            "from": self.context.signer.address,
            "nonce": nonce,
            "gasPrice": self.context.contracts.w3.eth.gas_price
        })
        signed_tx = self.contracts.w3.eth.account.sign_transaction(tx_params, self.context.signer.key)
        tx_hash = self.contracts.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        self.contracts.w3.eth.wait_for_transaction_receipt(tx_hash)
        return tx_hash.hex()
    
    def sign_order(self, req: ExecuteInsertOrder):
        return self.api.sign_order(req=req, chainId=self.api.chain_id, verifyingContract=self.contracts.positioning.address)
    
    def get_salt(self):
        date_salt = int(calendar.timegm(datetime.now().timetuple())) * 1000 * 1000
        
        maker_min_salt = self.context.contracts.matching_engine.functions.makerMinSalt(
            self.context.signer.address
        ).call()

        if maker_min_salt:
            order_salt = str(int(maker_min_salt) + date_salt)
        else:
            order_salt = str(date_salt)

        if self.prev_salt >= int(order_salt):
            self.prev_salt += 1
            return self.prev_salt
        else:
            self.prev_salt = int(order_salt)
            return int(order_salt)
    
    def send_order(self, base_asset_addr: str, is_short: bool, price_e6: str, base_amount: str, deadline: int):
        return self._send_order(
            base_asset_addr=base_asset_addr, 
            order_type=OrderType.ORDER.value, 
            is_short=is_short, 
            price_e6=price_e6, 
            base_amount=base_amount, 
            deadline=deadline,
            trigger_price_e6="0"
        )
    
    def send_trigger_order(self, order_type: OrderType, trigger_price_e6: str, base_asset_addr: str, is_short: bool, price_e6: str, base_amount: str, deadline: int):
        return self._send_order(
            base_asset_addr=base_asset_addr, 
            order_type=order_type, 
            is_short=is_short, 
            price_e6=price_e6, 
            base_amount=base_amount, 
            deadline=deadline,
            trigger_price_e6=trigger_price_e6
        )

    def _send_order(self, base_asset_addr: str, trigger_price_e6: str, order_type: OrderType, is_short: bool, price_e6: str, base_amount: str, deadline: int):
        salt = self.get_salt()
        print("salt:", salt)
        req = ExecuteInsertOrder(
            base_asset=ExecuteInsertOrderAsset(
                value=base_amount,
                virtual_token=base_asset_addr,
            ),
            # TODO: check if int too big error
            quote_asset=ExecuteInsertOrderAsset(
                value=str(int(Decimal(price_e6) * Decimal(base_amount) / Decimal(1e6))),
                virtual_token=self.contracts.quote_token.address,
            ),
            deadline=str(deadline),
            is_short=is_short,
            order_type=order_type,
            salt=str(salt),
            signature=None,
            trader=self.context.signer.address,
            trigger_price=trigger_price_e6,
        )
        signedMessage = self.sign_order(req=req)
        req.signature = signed_message_to_str(signedMessage)
        res = self.api.insert_order(req=req, chain=RelayerChain.VOT.value)
        return res


def create_volmex_client(network: VolmexNetwork, signer: Signer, chain_id: int, opts: Optional[VolmexClientContextOpts] = None, domain: str = None) -> VolmexClient:    
    (deployment, deployment_contracts, deployment_collateral, deployment_base_tokens) = load_deployment(network)
    domain="localhost:8080"
    chain_id=48124
    if opts is None:
        opts = VolmexClientContextOpts(
            api_endpoint=str(deployment.perps_api_url),
            deployment=deployment,
            deployment_base_token=deployment_base_tokens,
            deployment_collateral=deployment_collateral,
            deployment_contracts=deployment_contracts,
        )
    
    assert opts.api_endpoint, "api_endpoint not set!"
    assert opts.deployment, "deployment not set!"
    assert opts.deployment_contracts, "deployment_contracts not set!"
    assert opts.deployment_collateral, "deployment_collateral not set!"
    assert opts.deployment_base_token, "deployment_base_token not set!"
    
    api_client_opts = ApiClientOpts(
        url=opts.api_endpoint,
        chain_id=chain_id,
        domain=domain,
        signer=signer,
    )
    api_client = ApiClient(
        opts=api_client_opts
    )
    
    contracts = VolmexContracts(
        contracts_context=VolmexContractsContext(
            account_balance_addr=opts.deployment_contracts.account_balance_addr,
            collateral_manager_addr=opts.deployment_contracts.collateral_manager_addr,
            funding_rate_addr=opts.deployment_contracts.funding_rate_addr,
            matching_engine_addr=opts.deployment_contracts.matching_engine_addr,
            periphery_addr=opts.deployment_contracts.periphery_addr,
            perp_view_addr=opts.deployment_contracts.perp_view_addr,
            perpetual_oracle_addr=opts.deployment_contracts.perpetual_oracle_addr,
            positioning_addr=opts.deployment_contracts.positioning_addr,
            positioning_config_addr=opts.deployment_contracts.positioning_config_addr,
            quote_token_addr=opts.deployment_contracts.quote_token_addr,
            vault_addr=opts.deployment_contracts.vault_addr,
        ),
        node_url=opts.deployment.node_url,
    )
    volmex_client = VolmexClient(
        context=VolmexClientContext(
            signer=signer,
            api_client=api_client,
            contracts=contracts,
            deployment=opts.deployment,
            base_tokens=opts.deployment_base_token,
            collateral=opts.deployment_collateral,
        ),
    )
    volmex_client.login()
    return volmex_client