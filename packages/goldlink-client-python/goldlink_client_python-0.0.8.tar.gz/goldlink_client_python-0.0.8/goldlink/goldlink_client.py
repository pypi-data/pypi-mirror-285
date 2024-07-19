"""The GoldLink Client for interacting with the protocol."""

from web3 import Web3

from goldlink.modules.reader import Reader
from goldlink.modules.event_handler import EventHandler
from goldlink.modules.writer import Writer
from goldlink.modules.strategies.gmx_frf.gmx_frf_writer import GmxFrfWriter
from goldlink.modules.strategies.gmx_frf.gmx_frf_event_handler import GmxFrfEventHandler
from goldlink.modules.strategies.gmx_frf.gmx_frf_reader import GmxFrfReader
from goldlink.constants import NETWORK_ID_MAINNET, DEFAULT_API_TIMEOUT
from goldlink.signing.signer import SignWithWeb3, SignWithKey


class Client(object):
    '''
    Client users of the GoldLink-Client-Python will be interacting with the
    GoldLink Protocol through.
    '''

    def __init__(
        self,
        send_options=None,
        api_timeout=None,
        web3=None,
        network_id=None,
        private_key=None,
        web3_account=None,
        web3_provider=None,
        host=None,
        strategy_reserve=None,
        strategy_bank=None,
        strategy_account=None,
    ):
        # Set Contracts if input.
        self.strategy_reserve = strategy_reserve
        self.strategy_bank = strategy_bank
        self.strategy_account = strategy_account

        # Set API parameters if input.
        self.send_options = send_options or {}
        self.api_timeout = api_timeout or DEFAULT_API_TIMEOUT

        # Default web3 related parameters to None.
        self.web3 = None
        self.signer = None
        self.network_id = None

        # If web3 or web3 provider, set web3, signer, default address and network id.
        if web3 is not None or web3_provider is not None:
            if isinstance(web3_provider, str):
                web3_provider = Web3.HTTPProvider(
                    web3_provider, request_kwargs={'timeout': self.api_timeout}
                )
            self.web3 = web3 or Web3(web3_provider)
            self.signer = SignWithWeb3(self.web3)
            self.default_address = self.web3.eth.defaultAccount or None
            self.network_id = self.web3.net.version

        # If a private key was passed in or a web3 account, set signer and default address.
        if private_key is not None or web3_account is not None:
            # May override web3 or web3_provider configuration.
            key = private_key or web3_account.key
            self.signer = SignWithKey(key)
            self.default_address = self.signer.address

        # Make sure web3 is/can be set or revert.
        if not web3 and not host:
            raise Exception(
                'Web3 not passed in and cannot set web3 with no host or web3 provider.'
            )
        self.web3 = web3 or Web3(Web3.HTTPProvider(host))

        # Set default network ID.
        self.network_id = int(
            network_id or self.network_id or NETWORK_ID_MAINNET
        )

        # Initialize the reader and event handler modules. Other modules are initialized on
        # demand, if the necessary configuration options were provided.
        self._reader = Reader(
            web3=self.web3,
            network_id=self.network_id,
            strategy_bank=self.strategy_bank,
            strategy_reserve=self.strategy_reserve,
        )
        self._gmx_frf_reader = GmxFrfReader(
            web3=self.web3,
            network_id=self.network_id,
        )
        self._event_handler = EventHandler(web3=self.web3)
        self._gmx_frf_event_handler = GmxFrfEventHandler(web3=self.web3)
        self._writer = None
        self._gmx_frf_writer = None

    @property
    def reader(self):
        '''
        Get the reader module, used for reading from protocol.
        '''
        return self._reader

    @property
    def gmx_frf_reader(self):
        '''
        Get th GMX Funding-rate Farming reader module, used for reading from protocol for
        GMX Funding-rate Farming Strategy.
        '''
        return self._gmx_frf_reader

    @property
    def event_handler(self):
        '''
        Get the event handler module, used for handling events emitted from the protocol.
        '''
        return self._event_handler

    @property
    def gmx_frf_event_handler(self):
        '''
        Get the GMX Funding-rate Farming strategy event handler module, used for handling events
        emitted from the protocol for GMX Funding-rate Farming Strategy.
        '''
        return self._gmx_frf_event_handler

    @property
    def writer(self):
        '''
        Get the writer module, used for sending transactions to the protocol.
        '''
        if not self._writer:
            private_key = getattr(self.signer, '_private_key', None)
            if self.web3 and private_key:
                self._writer = Writer(
                    web3=self.web3,
                    private_key=private_key,
                    default_address=self.default_address,
                    send_options=self.send_options,
                    strategy_bank=self.strategy_bank,
                    strategy_reserve=self.strategy_reserve,
                    strategy_account=self.strategy_account,
                )
            else:
                raise Exception(
                    'Writer module is not supported since neither web3 ' +
                    'nor web3_provider was provided OR since neither ' +
                    'private_key nor web3_account was provided',
                )

        if self.strategy_account and not self._writer.strategy_account:
            self._writer.set_strategy_account(self.strategy_account)

        return self._writer

    @property
    def gmx_frf_writer(self):
        '''
        Get the GMX Funding-Rate Farming Writer module, used for sending strategy specific
        transactions to the protocol for GMX Funding-rate Farming Strategy.
        '''
        if not self._gmx_frf_writer:
            private_key = getattr(self.signer, '_private_key', None)
            if self.web3 and private_key:
                self._gmx_frf_writer = GmxFrfWriter(
                    web3=self.web3,
                    private_key=private_key,
                    default_address=self.default_address,
                    send_options=self.send_options,
                    strategy_account=self.strategy_account,
                )
            else:
                raise Exception(
                    'GMX Funding-Rate Farming Writer module is not supported since neither web3 ' +
                    'nor web3_provider was provided OR since neither ' +
                    'private_key nor web3_account was provided',
                )

        if self.strategy_account and not self._gmx_frf_writer.strategy_account:
            self._gmx_frf_writer.set_strategy_account(self.strategy_account)

        return self._gmx_frf_writer
