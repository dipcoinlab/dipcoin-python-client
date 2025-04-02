from pydantic import BaseModel

class ContractConstants(BaseModel):
    package_id: str
    admin_cap_id: str
    version_id: str
    global_id: str
    pool_registry_table_id: str

CONTRACT_CONSTANTS = {
    "testnet": ContractConstants(
        package_id="0xa21247f737d7ff2b2b2a03411f4693001b24ad2e217b863d1a3dbfadee9ddd3c",
        admin_cap_id="0x18f90fbdf9beb813b5a92131ecdc2da97e2954b92dcd893b909b196c3d2a672e",
        version_id="0xd4d49b0915459f013072d2c10139eeacac9865fedfc71108cc98565e446370fa",
        global_id="0x73ea415d3adb8c5ba4cc6322eaaf40f8d99ee54d979891df467ff478ba2154ff",
        pool_registry_table_id="0xeb87cbc1fb3cdd9d645f5b8793f30a4745637800babef11d37f4fd20569d60a8",
    )
}

POOLS = {
    "testnet": {
        "USDC_WSOL": "0x40b7f495f9933ed2f2e493a4f95876c2f2e9453dd67b877290d5df2aa4157aaf",
    }
}

TESTNET_FAUCET = {
    "package_id": "0x5c68f3d2ebfd711454da300d6abf3c7254dc9333cd138cdc68e158ebffd24483",
    "faucet_id": "0xce512917214d7e5b21b63f33ec2aebd923852bd3de27128c83f40d9a9f8bad35",
    "COIN_USDC": "0x5c68f3d2ebfd711454da300d6abf3c7254dc9333cd138cdc68e158ebffd24483::coins::USDC",
    "COIN_WSOL": "0x5c68f3d2ebfd711454da300d6abf3c7254dc9333cd138cdc68e158ebffd24483::coins::WSOL",
    "COIN_WETH": "0x5c68f3d2ebfd711454da300d6abf3c7254dc9333cd138cdc68e158ebffd24483::coins::WETH"
}

DEFAULT_SLIPPAGE = 0.005