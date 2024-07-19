"""General helpers for sending/handling blockchain queries."""

from web3 import Web3
import requests


def handle_event(event):
    '''
    Handle parsing a generic event.

    :param event: required
    :type event: Event

    :returns: AttributeDict
    '''
    return event[0]['args']


def send_raw_query(
        node_url,
        contract_address,
        function_signature,
        *args
):
    '''
    Send a raw query to a contract.

    :param node_url: required
    :type node_url: string

    :param contract_address: required
    :type contract_address: address

    :param function_signature: required
    :type function_signature: string

    :returns: any
    '''
    # Encode function call
    function_call_data = Web3.keccak(text=function_signature)[:4].hex()

    # Encode parameters
    for arg in args:
        hex_arg = Web3.toBytes(hexstr=arg)
        padded_hex_arg = hex_arg.rjust(32, b'\x00')
        function_call_data += padded_hex_arg.hex()

    # Construct `data` to send.
    data = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [
            {
                "to": contract_address,
                "data": function_call_data
            },
            "latest",
        ],
        "id": 1
    }

    # Send the JSON-RPC request
    response = requests.post(node_url, json=data)

    # Parse the response
    result_hex = response.json()["result"]
    result_decoded = int(result_hex, 16)

    return result_decoded
