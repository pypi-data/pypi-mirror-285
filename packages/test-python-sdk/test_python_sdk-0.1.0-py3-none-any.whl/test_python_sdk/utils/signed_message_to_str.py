
from hexbytes import HexBytes


def signed_message_to_str(signedMessage):
    """
    Function to convert a signed message to a string.
    
    Returns:
        str: The signed message as a string.
    """
    return HexBytes(signedMessage.signature).hex().__str__()