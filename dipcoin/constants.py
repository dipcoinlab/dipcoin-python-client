from pydantic import BaseModel

class ContractConstants(BaseModel):
    package_id: str
    admin_cap_id: str
    version_id: str
    global_id: str
    pool_registry_table_id: str

CONTRACT_CONSTANTS = {
    "testnet": ContractConstants(
        package_id="0xdd07cd4192c61a81f82718e0581c3c861e43e81ca26e46ae540276b95ed8d52d",
        admin_cap_id="0x1e291ad24506c86251dd03d94580b5292c0316c5e6c09688c4d1810b33b5ec17",
        version_id="0x99c565e4e87576433ffab5f66f7bce0db3d5f72785eed5384e681c22311af820",
        global_id="0x0a2ba97c9dad085366a35be0e48b51d353dc9b6e7ccfe723c4b2b56745d3e623",
        pool_registry_table_id="0x60347e948bb7b9c7f42715f66dbe4e5e5060bae19be1483e2b6daf1364fb1e42",
    )
}

NODE_RPC = {
    'testnet': 'https://fullnode.testnet.sui.io:443',
    'mainnet': 'https://fullnode.mainnet.sui.io:443',
}

TESTNET_FAUCET = {
    "package_id": "0x5c68f3d2ebfd711454da300d6abf3c7254dc9333cd138cdc68e158ebffd24483",
    "faucet_id": "0xce512917214d7e5b21b63f33ec2aebd923852bd3de27128c83f40d9a9f8bad35",
    "COIN_USDC": "0x5c68f3d2ebfd711454da300d6abf3c7254dc9333cd138cdc68e158ebffd24483::coins::USDC",
    "COIN_WSOL": "0x5c68f3d2ebfd711454da300d6abf3c7254dc9333cd138cdc68e158ebffd24483::coins::WSOL",
    "COIN_WETH": "0x5c68f3d2ebfd711454da300d6abf3c7254dc9333cd138cdc68e158ebffd24483::coins::WETH"
}

DEFAULT_SLIPPAGE = 0.005