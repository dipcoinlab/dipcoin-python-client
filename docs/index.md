# DipCoin Python SDK

DipCoin Python SDK is a powerful and easy-to-use library for interacting with the DipCoin Protocol on the Sui blockchain. This SDK provides a comprehensive set of tools for managing liquidity pools, performing swaps, and interacting with the DipCoin ecosystem.

## Features

- 🔄 Liquidity Pool Management
  - Add liquidity to pools
  - Remove liquidity from pools
  - Query pool information and IDs
- 💱 Token Swaps
  - Exact input swaps (swap_exact_in)
  - Exact output swaps (swap_exact_out)
- 🔍 Pool Discovery
  - Find pool IDs for token pairs
  - Query pool details and statistics
- ⚡ Transaction Management
  - Automatic coin splitting and merging
  - Transaction execution and status tracking

## Installation

```bash
pip install dipcoin
```

## Quick Start

Here's a simple example of how to use the DipCoin SDK:

```python
from dipcoin import DipcoinClient

async def main():
    # Initialize the client (defaults to testnet)
    client = DipcoinClient()
    
    # Get pool information
    pool = await client.get_pool("your_pool_id")
    
    # Add liquidity to a pool
    result = await client.add_liquidity(
        coin_x_type="0x2::sui::SUI",
        coin_y_type="0x2::usdc::USDC",
        coin_x_amount=1000000000,  # 1 SUI
        coin_y_amount=1000000,     # 1 USDC
        slippage=0.005             # 0.5% slippage
    )
    
    # Perform a swap
    swap_result = await client.swap_exact_in(
        coin_in_type="0x2::sui::SUI",
        coin_out_type="0x2::usdc::USDC",
        amount_in=1000000000,      # 1 SUI
        slippage=0.005             # 0.5% slippage
    )

# Run the async function
import asyncio
asyncio.run(main())
```

## Documentation

- [Tutorials](tutorials.md) - Step-by-step guides for common use cases
- [API Reference](reference.md) - Detailed documentation of all available methods and classes

## Support

For support, please join our community or open an issue on GitHub.
