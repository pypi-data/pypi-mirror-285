from typing import Optional
from pydantic import AnyUrl, Field
from test_python_sdk.utils.enum import StrEnum

from test_python_sdk.utils.model import VolmexBaseModel


class VolmexNetwork(StrEnum):
    """
    Enumeration representing various network environments for the Volmex protocol.
    """

    VOLMEX_CHAIN_TESTNET = "volmex-chain-testnet"


class VolmexAbiName(StrEnum):
    """
    Enumeration representing various contract names for which the ABI can be loaded in the Volmex protocol.
    """
    PERPETUAL_ORACLE = "PerpetualOracle"
    QUOTE_TOKEN = "QuoteToken"
    MATCHING_ENGINE = "MatchingEngine"
    FUNDING_RATE = "FundingRate"
    POSITIONING_CONFIG = "PositioningConfig"
    COLLATERAL_MANAGER = "CollateralManager"
    ACCOUNT_BALANCE = "AccountBalance"
    VAULT = "Vault"
    POSITIONING = "Positioning"
    PERIPHERY = "Periphery"
    PERP_VIEW = "PerpView"
    ERC20 = "ERC20"

class VolmexDeploymentContracts(VolmexBaseModel):
    """
    Class representing deployment data for Volmex protocol contracts.

    Attributes:
        node_url (AnyUrl): The URL of the node.
        
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
    perpetual_oracle_addr: str = Field(alias="PERPETUAL_ORACLE")
    quote_token_addr: str = Field(alias="QUOTE_TOKEN")
    matching_engine_addr: str = Field(alias="MATCHING_ENGINE")
    funding_rate_addr: str = Field(alias="FUNDING_RATE")
    positioning_config_addr: str = Field(alias="POSITIONING_CONFIG")
    collateral_manager_addr: str = Field(alias="COLLATERAL_MANAGER")
    account_balance_addr: str = Field(alias="ACCOUNT_BALANCE")
    vault_addr: str = Field(alias="VAULT")
    positioning_addr: str = Field(alias="POSITIONING")
    periphery_addr: str = Field(alias="PERIPHERY")
    perp_view_addr: str = Field(alias="PERP_VIEW")
    
class VolmexDeploymentBaseTokens(VolmexBaseModel):
    """
    Class representing deployment data for Volmex protocol base tokens.
    
    Attributes:
        eviv_addr (str): The address of the EVIV token.
        
        bviv_addr (str): The address of the BVIV token.
        
        ethusd_addr (str): The address of the ETHUSD token.
        
        btcusd_addr (str): The address of the BTCUSD token.
    """
    eviv_addr: str = Field(alias="EVIV")
    bviv_addr: str = Field(alias="BVIV")
    ethusd_addr: str = Field(alias="ETHUSD")
    btcusd_addr: str = Field(alias="BTCUSD")
    
class VolmexDeploymentCollateral(VolmexBaseModel):
    """
    Class representing deployment data for Volmex protocol collateral.
    
    Attributes:
        usdc_addr (str): The address of the USDC token.
        
        usdt_addr (str): The address of the USDT token.
        
        weth_addr (str): The address of the WETH token.
    """
    usdc_addr: str = Field(alias="USDC")
    usdt_addr: str = Field(alias="USDT")
    weth_addr: str = Field(alias="WETH")
    

class VolmexDeployment(VolmexBaseModel):
    """
    Class representing deployment data for the Volmex protocol.
    
    Attributes:
        node_url (AnyUrl): The URL of the node.
        
        perps_api_url (AnyUrl): The URL of the Perps Api
    """
    node_url: AnyUrl = Field(alias="nodeUrl")
    perps_api_url: AnyUrl = Field(alias="perpsApiUrl")