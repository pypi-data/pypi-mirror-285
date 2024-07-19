from eth_account import Account
from eth_account.signers.local import LocalAccount
from typing import Optional, Union
from pydantic.v1 import AnyUrl, BaseModel, root_validator, validator

PrivateKey = str
Signer = LocalAccount
# Signer = Union[LocalAccount, PrivateKey]

class ApiClientOpts(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    """
    Model defining the configuration options for the Api Client. It includes various parameters such as the URL,
    the signer, the chain ID, and others.

    Attributes:
        url (AnyUrl): The URL of the server.
        signer (Signer): The signer for the client, if any. It can either be a `LocalAccount` or a private key.
        chain_id (int): An optional network chain ID.
        domain (Optional[str]): An optional domain.
    """
    
    url: AnyUrl
    signer: Signer = None
    chain_id: int = None
    domain: Optional[str] = None
    

    @validator("url")
    def clean_url(cls, v: AnyUrl) -> str:
        """
        Cleans the URL input by removing trailing slashes.

        Args:
            v (AnyUrl): The input URL.

        Returns:
            str: The cleaned URL.
        """
        return v.rstrip("/")

    @validator("signer")
    def signer_to_local_account(cls, v: Optional[Signer]) -> Optional[LocalAccount]:
        """
        Validates and converts the signer to a LocalAccount instance.

        Args:
            v (Optional[Signer]): The signer instance or None.

        Returns:
            Optional[LocalAccount]: The LocalAccount instance or None.
        """
        if v is None or isinstance(v, LocalAccount):
            return v
        return Account.from_key(v)