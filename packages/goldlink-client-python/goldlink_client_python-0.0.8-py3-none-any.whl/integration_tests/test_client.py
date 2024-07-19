'''Integration tests for client. Assumes anvil is running.

Usage: python -m pytest integration_tests/test_client.py
'''

import pytest
from web3 import Web3
from goldlink import Client
from integration_tests.constants import WEB_PROVIDER_URL
from goldlink.constants import CONTRACTS, ADDRESS_MANAGER, NETWORK_ID_ANVIL

ADDRESS_MANAGER_ADDRESS = CONTRACTS[ADDRESS_MANAGER][NETWORK_ID_ANVIL]


class TestClient():

    def test_reader_no_host_or_web3(self):
        with pytest.raises(Exception) as excinfo:
            Client()
        assert str(excinfo.value) == '''
            Web3 not passed in and cannot set
            web3 with no host or web3 provider.
        '''

    def test_reader_web3(self):
        client = Client(
            network_id=NETWORK_ID_ANVIL,
            web3=Web3(Web3.HTTPProvider(WEB_PROVIDER_URL)),
        )
        assert client.reader.get_address_manager() == ADDRESS_MANAGER_ADDRESS

    def test_reader_host(self):
        client = Client(
            network_id=NETWORK_ID_ANVIL,
            host=WEB_PROVIDER_URL,
        )
        assert client.reader.get_address_manager() == ADDRESS_MANAGER_ADDRESS
