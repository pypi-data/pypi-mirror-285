# Install
 
You can install the SDK via pip:

```
pip install volmex-python-sdk
```

# Basic Usage

## Basic Imports

```
from eth_account import Account
from sanity import CHAIN_ID, NETWORK, SIGNER_PRIVATE_KEY
from test_python_sdk.api_client.types.execute import ExecuteInsertOrder, ExecuteInsertOrderAsset
from test_python_sdk.api_client.types.models import OrderType, RelayerChain
from test_python_sdk.client import VolmexClient, create_volmex_client
from eth_account.signers.local import LocalAccount
from test_python_sdk.utils.signed_message_to_str import signed_message_to_str
```
## Connect Account

```
signer: LocalAccount = Account.from_key(SIGNER_PRIVATE_KEY)

volmex_client: VolmexClient = create_volmex_client(
    network=NETWORK,
    signer=signer,
)

volmex_client.login()
```

## Submit an Order

```


volmex_client.send_order(
    base_asset_addr=volmex_client.deployment_base_token.bviv_addr,
    is_short=False,
    price_e6="40000000000000000000",
    base_amount="1000000000000000000",
    deadline=1820012100
)
```

## Interacting with the Contracts
```
print("getLiquidationPenaltyRatio:", volmex_client.contracts.positioning_config.functions.getLiquidationPenaltyRatio().call())
```


# commands


To initialize virtual environment
```
poetry shell
```

To install dependencies

```

poetry install
```



To publish
```
poetry publish
```


# Run sanity checks

- `poetry run api-sanity`: run sanity checks for `api_client`
- `poetry run contracts-sanity`: run sanity checks for `contracts`
- `poetry run client-sanity`: run sanity checks for `client`

### Build Docs

To build the docs locally run:

```
$ poetry run sphinx-build docs/source docs/build
```