import json
from pathlib import Path
from test_python_sdk.contracts.types import (
    VolmexAbiName,
    VolmexDeployment,
    VolmexDeploymentBaseTokens,
    VolmexDeploymentCollateral,
    VolmexDeploymentContracts,
    VolmexNetwork,
)
from test_python_sdk.utils.model import ensure_data_type, parse_enum_value


def load_abi(abi_name: VolmexAbiName) -> list[dict]:
    """
    Load the Application Binary Interface (ABI) for a given contract.

    Args:
        abi_name (VolmexAbiName): The name of the contract for which the ABI is loaded.

    Returns:
        list[dict]: A list of dictionaries representing the ABI of the contract.
    """
    file_path = Path(__file__).parent / "abis" / f"{parse_enum_value(abi_name)}.json"
    return ensure_data_type(_load_json(file_path), list)


def load_deployment(network: VolmexNetwork):
    """
    Load the deployment data for a given network.

    Args:
        network (VolmexNetwork): The network for which the deployment data is loaded.

    Returns:
        VolmexDeployment: An instance of VolmexDeployment containing the loaded deployment data.
    """
    
    file_path_base = (
        Path(__file__).parent
        / "deployments"
        / f"{parse_enum_value(network)}"
    )
    
    file_path_base_tokens = (
        file_path_base
        / "baseTokens.json"
    )
    file_path_collateral = (
        file_path_base
        / "collateral.json"
    )
    file_path_contracts = (
        file_path_base
        / "contracts.json"
    )
    
    file_path_urls = (
        file_path_base
        / "urls.json"
    )
    return (VolmexDeployment(
                # **_load_json(file_path_contracts), 
                **_load_json(file_path_urls), 
                # **_load_json(file_path_base_tokens), 
                # **_load_json(file_path_collateral)
            ),
            VolmexDeploymentContracts(**_load_json(file_path_contracts)),
            VolmexDeploymentCollateral(**_load_json(file_path_collateral)),
            VolmexDeploymentBaseTokens(**_load_json(file_path_base_tokens))
        )

    # return VolmexDeploymentBaseTokens(**_load_json(file_path_base_tokens))
    # return VolmexDeployment(**_load_json(file_path_contracts), **_load_json(file_path_urls))
    # return (VolmexDeployment(**_load_json(file_path_contracts), **_load_json(file_path_urls)), VolmexDeploymentBaseTokens(**_load_json(file_path_base_tokens)), VolmexDeploymentCollateral(**_load_json(file_path_collateral)))


def _load_json(file_path: Path) -> dict:
    """
    Load a JSON file.

    Args:
        file_path (Path): The path to the JSON file.

    Returns:
        dict: The content of the JSON file as a dictionary.
    """
    with open(file_path, "r") as f:
        data = json.load(f)
    return data
