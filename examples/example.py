import asyncio
import dipcoin
from dipcoin.constants import CONTRACT_CONSTANTS, TESTNET_FAUCET

async def test_pool(client: dipcoin.DipcoinClient):
    print("Testing pool")
    print(await client.get_pool_id(TESTNET_FAUCET['COIN_USDC'], TESTNET_FAUCET['COIN_WSOL']))

async def test_add_liquidity(client: dipcoin.DipcoinClient):
    print("Testing add liquidity")
    coin_x_type = TESTNET_FAUCET['COIN_USDC']
    coin_y_type = TESTNET_FAUCET['COIN_WSOL']
    print(await client.add_liquidity(coin_x_type, coin_y_type, 1000000, 1000000))

async def test_remove_liquidity(client: dipcoin.DipcoinClient):
    print("Testing remove liquidity")
    coin_x_type = TESTNET_FAUCET['COIN_USDC']
    coin_y_type = TESTNET_FAUCET['COIN_WSOL']
    print(await client.remove_liquidity(coin_x_type, coin_y_type, 100000))

async def test_swap_exact_in(client: dipcoin.DipcoinClient):
    print("Testing swap exact in")
    print(await client.swap_exact_in(TESTNET_FAUCET['COIN_USDC'], TESTNET_FAUCET['COIN_WSOL'], 100000))
    print(await client.swap_exact_in(TESTNET_FAUCET['COIN_WSOL'], TESTNET_FAUCET['COIN_USDC'], 200000))

async def test_swap_exact_out(client: dipcoin.DipcoinClient):
    print("Testing swap exact out")
    print(await client.swap_exact_out(TESTNET_FAUCET['COIN_USDC'], TESTNET_FAUCET['COIN_WSOL'], 100000))
    print(await client.swap_exact_out(TESTNET_FAUCET['COIN_WSOL'], TESTNET_FAUCET['COIN_USDC'], 200000))
    
async def test_all(client: dipcoin.DipcoinClient):
    await test_pool(client)
    await test_add_liquidity(client)
    await test_remove_liquidity(client)
    await test_swap_exact_in(client)
    await test_swap_exact_out(client)

if __name__ == "__main__":
    client = dipcoin.DipcoinClient(network="testnet")
    asyncio.run(test_all(client))



