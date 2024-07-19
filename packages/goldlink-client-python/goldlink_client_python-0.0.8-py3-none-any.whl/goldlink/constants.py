"""Constants used in the GoldLink Client."""

# ------------  Network IDs ------------
NETWORK_ID_MAINNET = 42161
NETWORK_ID_FUJI = 43113

# ------------  Provider URLs ------------

WEB_PROVIDER_URL_ARBITRUM_MAINNET = 'https://arb1.arbitrum.io/rpc'
WEB_PROVIDER_URL_FUJI = 'https://rpc.ankr.com/avalanche_fuji'

# ------------ Signature Types ------------
SIGNATURE_TYPE_NO_PREPEND = 0
SIGNATURE_TYPE_DECIMAL = 1
SIGNATURE_TYPE_HEXADECIMAL = 2

# ------------ Assets ------------
ASSET_USDC = 'USDC'

# ------------ Core Contracts ------------
CONTROLLER = 'Controller'
BANK = 'Bank'
RESERVE = 'Reserve'

# ------------ Transactions ------------
DEFAULT_GAS_AMOUNT = 2500000
DEFAULT_GAS_MULTIPLIER = 1.5
DEFAULT_GAS_PRICE = 4000000000
DEFAULT_GAS_PRICE_ADDITION = 3
MAX_SOLIDITY_UINT = 115792089237316195423570985008687907853269984665640564039457584007913129639935  # noqa: E501

CONTRACTS = {
    ASSET_USDC: {
        NETWORK_ID_MAINNET: '0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
        NETWORK_ID_FUJI: '0x3eBDeaA0DB3FfDe96E7a0DBBAFEC961FC50F725F'
    },
    CONTROLLER: {
        NETWORK_ID_MAINNET: '0xB4E29a1a0E6f9dB584447e988Ce15d48a1381311',
        NETWORK_ID_FUJI: '0x62be6F58cD141542d3e0d1CB1814e2464cbf3462'
    },
    BANK: {
        NETWORK_ID_MAINNET: '0x479889160FEECe9C0fB0FDDF3b45312f54D719CC',
        NETWORK_ID_FUJI: '0xfc8D0b15999b040A2cF1C6fD4ABF18e6f70E84C7'
    },
    RESERVE: {
        NETWORK_ID_MAINNET: '0xd8dD54dF1A7d2EA022B983756d8a481Eea2a382a',
        NETWORK_ID_FUJI: '0x4b927EC02cFAB1237eA9e13d5568850Dc0FDFBF5'
    }
}
COLLATERAL_TOKEN_DECIMALS = 6
DEFAULT_GAS_PRICE_ADDITION = 3

# ------------ API Defaults ------------
DEFAULT_API_TIMEOUT = 3000

# ------------ GoldLink Protocol ABI Paths ------------
ERC20 = 'abi/erc20.json'
STRATEGY_ACCOUNT_ABI = 'abi/strategy-account.json'
STRATEGY_BANK_ABI = 'abi/strategy-bank.json'
STRATEGY_RESERVE_ABI = 'abi/strategy-reserve.json'

# ------------ GoldLink Protocol GMX FRF ABI Paths ------------

GMX_FRF_STRATEGY_ACCOUNT_ABI = 'abi/gmx-frf-strategy-account.json'
GMX_FRF_STRATEGY_MANAGER_ABI = 'abi/gmx-frf-strategy-manager.json'
GMX_FRF_ACCOUNT_GETTERS_ABI = 'abi/gmx-frf-account-getters.json'
GMX_V2_READER_ABI = 'abi/gmx-v2-reader.json'
IGMX_V2_DATASTORE_ABI = 'abi/igmx-v2-datastore.json'
