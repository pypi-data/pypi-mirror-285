from dataclasses import dataclass
from typing import Optional
from test_python_sdk.api_client import ApiClient
from test_python_sdk.contracts import VolmexContracts
from eth_account.signers.local import LocalAccount
from test_python_sdk.contracts.types import VolmexDeployment, VolmexDeploymentBaseTokens, VolmexDeploymentCollateral, VolmexDeploymentContracts
from test_python_sdk.utils.model import VolmexBaseModel


class VolmexClientContext(VolmexBaseModel):
    """
    Context required to use the Volmex client.
    """

    signer: Optional[LocalAccount]
    api_client: ApiClient
    deployment: VolmexDeployment
    contracts: VolmexContracts
    base_tokens: VolmexDeploymentBaseTokens
    collateral: VolmexDeploymentCollateral

class VolmexClientContextOpts(VolmexBaseModel):
    api_endpoint: str
    deployment: VolmexDeployment
    deployment_contracts: VolmexDeploymentContracts
    deployment_collateral: VolmexDeploymentCollateral
    deployment_base_token: VolmexDeploymentBaseTokens