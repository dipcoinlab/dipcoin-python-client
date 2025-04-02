import asyncio
import dipcoin
from dipcoin.constants import CONTRACT_CONSTANTS, TESTNET_FAUCET, POOLS

async def test_pool(client: dipcoin.DipcoinClient):
    instance = await client.get_pool_id(TESTNET_FAUCET['COIN_USDC'], TESTNET_FAUCET['COIN_WSOL'])
    print(instance)

async def test_add_liquidity(client: dipcoin.DipcoinClient):
    pool_id = POOLS['testnet']['USDC_WSOL']
    coin_x_type = TESTNET_FAUCET['COIN_USDC']
    coin_y_type = TESTNET_FAUCET['COIN_WSOL']
    instance = await client.add_liquidity(pool_id, coin_x_type, coin_y_type, 1000000, 1000000)
    print(instance)

async def test_remove_liquidity(client: dipcoin.DipcoinClient):
    pool_id = POOLS['testnet']['USDC_WSOL']
    coin_x_type = TESTNET_FAUCET['COIN_USDC']
    coin_y_type = TESTNET_FAUCET['COIN_WSOL']
    instance = await client.remove_liquidity(pool_id, coin_x_type, coin_y_type, 100000)
    print(instance)

async def test_swap_exact_in(client: dipcoin.DipcoinClient):
    pool_id = POOLS['testnet']['USDC_WSOL']
    print(await client.swap_exact_in(pool_id, TESTNET_FAUCET['COIN_USDC'], TESTNET_FAUCET['COIN_WSOL'], 100000))
    print(await client.swap_exact_in(pool_id, TESTNET_FAUCET['COIN_WSOL'], TESTNET_FAUCET['COIN_USDC'], 200000))

async def test_swap_exact_out(client: dipcoin.DipcoinClient):
    pool_id = POOLS['testnet']['USDC_WSOL']
    print(await client.swap_exact_out(pool_id, TESTNET_FAUCET['COIN_USDC'], TESTNET_FAUCET['COIN_WSOL'], 100000))
    print(await client.swap_exact_out(pool_id, TESTNET_FAUCET['COIN_WSOL'], TESTNET_FAUCET['COIN_USDC'], 200000))

if __name__ == "__main__":
    client = dipcoin.DipcoinClient()
    # asyncio.run(test_add_liquidity(client))
    # asyncio.run(test_remove_liquidity(client))
    # asyncio.run(test_swap_exact_in(client))
    asyncio.run(test_swap_exact_out(client))




