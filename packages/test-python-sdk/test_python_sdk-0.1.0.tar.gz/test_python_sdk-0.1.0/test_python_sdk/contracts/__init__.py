from pydantic import BaseModel
from typing import Callable
from test_python_sdk.contracts.loader import load_abi
from web3 import Web3
from web3.types import TxParams
from web3.contract import Contract
from web3.contract.contract import ContractFunction
from eth_account.signers.local import LocalAccount
from test_python_sdk.contracts.types import *

class VolmexContractsContext(BaseModel):
    """
    Holds the context for various Volmex contracts.

    Attributes:
        perpetual_oracle_addr (str): The address of the perpetual oracle contract.
        
        quote_token_addr (str): The address of the quote token contract.
        
        matching_engine_addr (str): The address of the matching engine contract.
        
        funding_rate_addr (str): The address of the funding rate contract.
        
        positioning_config_addr (str): The address of the positioning config contract.
        
        collateral_manager_addr (str): The address of the collateral manager contract.
        
        account_balance_addr (str): The address of the account balance contract.
        
        vault_addr (str): The address of the vault contract.
        
        positioning_addr (str): The address of the positioning contract.
        
        periphery_addr (str): The address of the periphery contract.
        
        perp_view_addr (str): The address of the perpetual view contract.
    """
    perpetual_oracle_addr: str
    quote_token_addr: str
    matching_engine_addr: str
    funding_rate_addr: str
    positioning_config_addr: str
    collateral_manager_addr: str
    account_balance_addr: str
    vault_addr: str
    positioning_addr: str
    periphery_addr: str
    perp_view_addr: str

class Factory(BaseModel):
    erc20: Callable[[str], Contract]
class VolmexContracts:
    """
    Encapsulates the set of Volmex contracts required for querying and executing.
    """
    
    w3: Web3
    network: VolmexNetwork
    contracts_context: VolmexContractsContext
    perpetual_oracle: Contract
    quote_token: Contract
    matching_engine: Contract
    funding_rate: Contract
    positioning_config: Contract
    collateral_manager: Contract
    account_balance: Contract
    vault: Contract
    positioning: Contract
    periphery: Contract
    perp_view: Contract
    factory: Factory
    
    def __init__(self, node_url: str, contracts_context: VolmexContractsContext):
        """
        Initializes the VolmexContracts instance.

        Args:
            node_url (str): The URL of the node.
            
            contracts_context (VolmexContractsContext): The context for various Volmex contracts.
        """
        self.w3 = Web3(Web3.HTTPProvider(node_url))
        self.contracts_context = VolmexContractsContext.parse_obj(contracts_context)
        self.perpetual_oracle : Contract = self.w3.eth.contract(address=contracts_context.perpetual_oracle_addr, abi=load_abi(VolmexAbiName.PERPETUAL_ORACLE))
        self.quote_token : Contract = self.w3.eth.contract(address=contracts_context.quote_token_addr, abi=load_abi(VolmexAbiName.QUOTE_TOKEN))
        self.matching_engine : Contract = self.w3.eth.contract(address=contracts_context.matching_engine_addr, abi=load_abi(VolmexAbiName.MATCHING_ENGINE))
        self.funding_rate : Contract = self.w3.eth.contract(address=contracts_context.funding_rate_addr, abi=load_abi(VolmexAbiName.FUNDING_RATE))
        self.positioning_config : Contract = self.w3.eth.contract(address=contracts_context.positioning_config_addr, abi=load_abi(VolmexAbiName.POSITIONING_CONFIG))
        self.collateral_manager : Contract = self.w3.eth.contract(address=contracts_context.collateral_manager_addr, abi=load_abi(VolmexAbiName.COLLATERAL_MANAGER))
        self.account_balance : Contract = self.w3.eth.contract(address=contracts_context.account_balance_addr, abi=load_abi(VolmexAbiName.ACCOUNT_BALANCE))
        self.vault : Contract = self.w3.eth.contract(address=contracts_context.vault_addr, abi=load_abi(VolmexAbiName.VAULT))
        self.positioning : Contract = self.w3.eth.contract(address=contracts_context.positioning_addr, abi=load_abi(VolmexAbiName.POSITIONING))
        self.periphery : Contract = self.w3.eth.contract(address=contracts_context.periphery_addr, abi=load_abi(VolmexAbiName.PERIPHERY))
        self.perp_view : Contract = self.w3.eth.contract(address=contracts_context.perp_view_addr, abi=load_abi(VolmexAbiName.PERP_VIEW))
        self.factory = Factory(
            erc20=lambda addr: self.w3.eth.contract(address=addr, abi=load_abi(VolmexAbiName.ERC20))
        )
        
    def deposit(self, collateral: str, amount: int, signer: LocalAccount) -> str:
        """
        Deposits funds into the vault.

        Args:
            amount (int): The amount to be deposited.

            signer (LocalAccount): The local account object that will sign the transaction. It should contain the private key.

        Returns:
            str: The hexadecimal representation of the transaction hash.
        """
        return self.execute(self.periphery.functions.depositToVault(0, collateral, amount, signer.address), signer)
    
    def withdraw(self, collateral: str, amount: int, signer: LocalAccount) -> str:
        """
        Withdraws funds from the vault.

        Args:
            amount (int): The amount to be withdrawn.

            signer (LocalAccount): The local account object that will sign the transaction. It should contain the private key.

        Returns:
            str: The hexadecimal representation of the transaction hash.
        """
        return self.execute(self.periphery.functions.withdrawFromVault(0, collateral, amount), signer)
    
    # TODO: Nice to have - add cancel and cancel all functions
        
    def execute(self, func: ContractFunction, signer: LocalAccount) -> str:
        """
        Executes a smart contract function.

        This method builds a transaction for a given contract function, signs the transaction with the provided signer's private key,
        sends the raw signed transaction to the network, and waits for the transaction to be mined.

        Args:
            func (ContractFunction): The contract function to be executed.

            signer (LocalAccount): The local account object that will sign the transaction. It should contain the private key.

        Returns:
            str: The hexadecimal representation of the transaction hash.

        Raises:
            ValueError: If the transaction is invalid, the method will not catch the error.
            TimeExhausted: If the transaction receipt isn't available within the timeout limit set by the Web3 provider.
        """
        tx = func.build_transaction(self._build_tx_params(signer))
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=signer.key)
        signed_tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        self.w3.eth.wait_for_transaction_receipt(signed_tx_hash)
        return signed_tx_hash.hex()

    def _build_tx_params(self, signer: LocalAccount) -> TxParams:
        tx_params: TxParams = {
            "from": signer.address,
            "nonce": self.w3.eth.get_transaction_count(signer.address),
        }
        # needs_gas_price = False
        # if needs_gas_price or os.getenv("CLIENT_MODE") in ["devnet"]:
        #     tx_params["gasPrice"] = self.w3.eth.gas_price
        return tx_params