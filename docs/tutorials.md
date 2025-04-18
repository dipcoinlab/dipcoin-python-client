# Tutorials

This guide provides step-by-step tutorials for common use cases with the DipCoin SDK.

## Working with Liquidity Pools

### Finding a Pool

Before interacting with a pool, you'll need to find its ID. Here's how to do it:

```python
from dipcoin import DipcoinClient

async def find_pool():
    client = DipcoinClient()
    
    # Define the token types you want to trade
    coin_x_type = "0x2::sui::SUI"
    coin_y_type = "0x2::usdc::USDC"
    
    # Get the pool ID
    pool_id = await client.get_pool_id(coin_x_type, coin_y_type)
    
    if pool_id:
        print(f"Found pool: {pool_id}")
    else:
        print("No pool found for this pair")
```

### Adding Liquidity

Adding liquidity to a pool is a common operation. Here's how to do it:

```python
from dipcoin import DipcoinClient

async def add_liquidity_example():
    client = DipcoinClient()
    
    # Pool parameters
    coin_x_type = "0x2::sui::SUI"
    coin_y_type = "0x2::usdc::USDC"
    
    # Amounts to add (in smallest units)
    coin_x_amount = 1000000000  # 1 SUI
    coin_y_amount = 1000000     # 1 USDC
    
    # Add liquidity with 0.5% slippage tolerance
    result = await client.add_liquidity(
        coin_x_type=coin_x_type,
        coin_y_type=coin_y_type,
        coin_x_amount=coin_x_amount,
        coin_y_amount=coin_y_amount,
        slippage=0.005
    )
    
    if result.status:
        print(f"Successfully added liquidity! Transaction ID: {result.digest}")
    else:
        print(f"Failed to add liquidity: {result.error}")
```

### Removing Liquidity

To remove liquidity from a pool:

```python
from dipcoin import DipcoinClient

async def remove_liquidity_example():
    client = DipcoinClient()
    
    # Pool parameters
    coin_x_type = "0x2::sui::SUI"
    coin_y_type = "0x2::usdc::USDC"
    
    # Amount of LP tokens to remove
    lp_amount = 1000000
    
    # Remove liquidity
    result = await client.remove_liquidity(
        coin_x_type=coin_x_type,
        coin_y_type=coin_y_type,
        lp_amount=lp_amount,
        slippage=0.005
    )
    
    if result.status:
        print(f"Successfully removed liquidity! Transaction ID: {result.digest}")
    else:
        print(f"Failed to remove liquidity: {result.error}")
```

## Performing Swaps

### Exact Input Swap

When you know exactly how much of the input token you want to spend:

```python
from dipcoin import DipcoinClient

async def exact_input_swap():
    client = DipcoinClient()
    
    # Token types
    coin_in_type = "0x2::sui::SUI"
    coin_out_type = "0x2::usdc::USDC"
    
    # Amount of input token to spend
    amount_in = 1000000000  # 1 SUI
    
    # Perform the swap with 0.5% slippage tolerance
    result = await client.swap_exact_in(
        coin_in_type=coin_in_type,
        coin_out_type=coin_out_type,
        amount_in=amount_in,
        slippage=0.005
    )
    
    if result.status:
        print(f"Swap successful! Transaction ID: {result.digest}")
    else:
        print(f"Swap failed: {result.error}")
```

### Exact Output Swap

When you know exactly how much of the output token you want to receive:

```python
from dipcoin import DipcoinClient

async def exact_output_swap():
    client = DipcoinClient()
    
    # Token types
    coin_in_type = "0x2::sui::SUI"
    coin_out_type = "0x2::usdc::USDC"
    
    # Amount of output token to receive
    amount_out = 1000000  # 1 USDC
    
    # Perform the swap with 0.5% slippage tolerance
    result = await client.swap_exact_out(
        coin_in_type=coin_in_type,
        coin_out_type=coin_out_type,
        amount_out=amount_out,
        slippage=0.005
    )
    
    if result.status:
        print(f"Swap successful! Transaction ID: {result.digest}")
    else:
        print(f"Swap failed: {result.error}")
```

## Error Handling

The SDK provides detailed error information when operations fail. Here's how to handle errors properly:

```python
from dipcoin import DipcoinClient
from dipcoin.exceptions import PoolNotFound

async def error_handling_example():
    client = DipcoinClient()
    
    try:
        result = await client.add_liquidity(
            coin_x_type="0x2::sui::SUI",
            coin_y_type="0x2::usdc::USDC",
            coin_x_amount=1000000000,
            coin_y_amount=1000000
        )
        
        if not result.status:
            print(f"Operation failed: {result.error}")
            
    except PoolNotFound as e:
        print(f"Pool not found: {e.message}")
        print(f"Token pair: {e.coin_x_type}/{e.coin_y_type}")
    except ValueError as e:
        print(f"Invalid input: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
```

Common exceptions you might encounter:

- `PoolNotFound`: Raised when attempting to interact with a pool that doesn't exist
- `ValueError`: Raised for invalid input parameters (e.g., negative amounts, invalid slippage)
- `Exception`: Raised for other unexpected errors

## Best Practices

1. **Always Check Transaction Status**: Verify the `status` field in the result object before proceeding.
2. **Use Appropriate Slippage**: Set slippage tolerance based on market conditions and your risk tolerance.
3. **Handle Errors Gracefully**: Implement proper error handling for failed transactions.
4. **Use Async/Await**: The SDK is built with async/await support for better performance.
5. **Test on Testnet**: Always test your code on testnet before deploying to mainnet.
6. **Monitor Coin Balances**: Ensure you have sufficient balance before performing operations.
7. **Understand Token Decimals**: Be aware of the decimal places for different tokens when specifying amounts.
