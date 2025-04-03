"""Dipcoin Python SDK"""
from typing import Dict, Any
from decimal import Decimal

from pysui import handle_result
from pysui import PysuiConfiguration, handle_result, AsyncGqlClient
from pysui.sui.sui_pgql import pgql_query as qn
from pysui.sui.sui_pgql.pgql_types import ObjectReadGQL, NoopGQL
from pysui.sui.sui_pgql.pgql_async_txn import AsyncSuiTransaction as SuiTransaction

from .types import Pool
from .utils import format_lp_name, sort_type, sort_and_get_lp_type
from .constants import CONTRACT_CONSTANTS, DEFAULT_SLIPPAGE
from .math import calc_optimal_coin_values, get_amount_out, get_amount_in

class DipcoinClient:
    """A client for interacting with the Dipcoin Protocol on Sui blockchain.
    
    This client provides methods to interact with Dipcoin's liquidity pools,
    including adding/removing liquidity and performing swaps.
    
    Attributes:
        network (str): The network to connect to (e.g., "testnet", "mainnet")
        client (AsyncGqlClient): The Sui GraphQL client instance
    """

    def __init__(
        self, 
        network: str = "testnet"
    ):
        """Initialize the Dipcoin client.
        
        Args:
            network (str, optional): The network to connect to. Defaults to "testnet".
        """
        cfg = PysuiConfiguration(group_name=PysuiConfiguration.SUI_GQL_RPC_GROUP )
        self.client = AsyncGqlClient(pysui_config=cfg,write_schema=False)
        self.network = network

    async def get_pool(self, pool_id: str) -> Pool | None:
        """Retrieve information about a specific liquidity pool.
        
        Args:
            pool_id (str): The unique identifier of the pool to query.
            
        Returns:
            Pool | None: A Pool object containing the pool's information if found,
                        None if the pool doesn't exist.
                        
        Raises:
            Exception: If there's an error parsing the pool data or an unknown error occurs.
        """
        qres = await self.client.execute_query_node(
            with_node=qn.GetObject(
                object_id=pool_id
            )
        )
        res = handle_result(qres)
        if isinstance(res, ObjectReadGQL):
            try:
                return Pool.from_gql_response(res.content)
            except:
                raise Exception(f"Unknown error: {res}")
        elif isinstance(res, NoopGQL):
            return None
        else:
            raise Exception(f"Unknown error: {res}")
        
    async def get_pool_id(self, coin_x_type: str, coin_y_type: str) -> str | None:
        """Get the pool ID for a given pair of tokens.
        
        Args:
            coin_x_type (str): The type of the first token in the pair.
            coin_y_type (str): The type of the second token in the pair.
            
        Returns:
            str | None: The pool ID if found, None if no pool exists for the given pair.
        """
        # TODO: Implement pool ID retrieval logic
        pass

    async def add_liquidity(
        self,
        pool_id: str,
        coin_x_type: str,
        coin_y_type: str,
        coin_x_amount: int,
        coin_y_amount: int,
        slippage: float = DEFAULT_SLIPPAGE,
    ) -> Dict[str, Any]:
        """Add liquidity to a pool.
        
        This method allows users to provide liquidity to a pool by depositing both tokens
        in the pair. The amounts are automatically adjusted to maintain the pool's price ratio.
        
        Args:
            pool_id (str): The ID of the pool to add liquidity to.
            coin_x_type (str): The type of the first token.
            coin_y_type (str): The type of the second token.
            coin_x_amount (int): The amount of the first token to deposit.
            coin_y_amount (int): The amount of the second token to deposit.
            slippage (float, optional): The maximum acceptable slippage in percentage.
                                      Defaults to DEFAULT_SLIPPAGE (0.5%).
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - tx_id (str): The transaction ID if successful, empty string if failed
                - status (bool): True if the transaction was successful, False otherwise
                - error (str, optional): Error message if the transaction failed
        
        Raises:
            ValueError: If amounts are invalid or slippage is out of range
        """
        try:
            # Ensure correct order of typeX and typeY
            new_type_x, new_type_y = sort_type(coin_x_type, coin_y_type)
            is_change = new_type_x != coin_x_type
            coin_x_type = new_type_x
            coin_y_type = new_type_y
            
            if is_change:
                coin_x_amount, coin_y_amount = coin_y_amount, coin_x_amount

            # Validate input amounts
            if coin_x_amount <= 0 or coin_y_amount <= 0:
                raise ValueError("Amount must be greater than 0")
            if slippage >= 1.0 or slippage < 0.0:
                raise ValueError(r"Slippage must be less than 100% and greater than 0%")

            # Get pool information
            pool = await self.get_pool(pool_id)
            if not pool:
                raise ValueError("Failed to get pool info")

            # Calculate optimal amounts
            coin_x_desired, coin_y_desired = calc_optimal_coin_values(
                Decimal(str(coin_x_amount)),
                Decimal(str(coin_y_amount)),
                Decimal(str(pool.bal_x.value)),
                Decimal(str(pool.bal_y.value))
            )
            # Calculate minimum accepted amounts (considering slippage)
            coin_x_min = int(coin_x_desired * Decimal(1.0 - slippage))
            coin_y_min = int(coin_y_desired * Decimal(1.0 - slippage))

            # Create transaction
            txn = SuiTransaction(client=self.client)
            
            # Split X token
            split_coin_x = await self._split_coin(
                self.client.config.active_address,
                coin_x_type,
                coin_x_amount,
                txn
            )
            
            # Split Y token
            split_coin_y = await self._split_coin(
                self.client.config.active_address,
                coin_y_type,
                coin_y_amount,
                txn
            )

            # Call contract to add liquidity
            await txn.move_call(
                target=f"{CONTRACT_CONSTANTS[self.network].package_id}::router::add_liquidity",
                arguments=[
                    CONTRACT_CONSTANTS[self.network].version_id,
                    CONTRACT_CONSTANTS[self.network].global_id,
                    pool_id,
                    split_coin_x,
                    coin_x_min,
                    split_coin_y,
                    coin_y_min
                ],
                type_arguments=[coin_x_type, coin_y_type]
            )
            # Execute transaction
            tx_data = await txn.build_and_sign()
            tx_result = await txn.client.execute_query_node(
                with_node=qn.ExecuteTransaction(**tx_data)
            )
            tx_result = handle_result(tx_result)

            return {
                "tx_id": tx_result.digest,
                "status": True
            }

        except Exception as e:
            return {
                "tx_id": "",
                "status": False,
                "error": str(e)
            }

    async def _split_coin(
        self,
        owner_address: str,
        coin_type: str,
        amount: int,
        txn: SuiTransaction
    ) -> Dict[str, Any]:
        """Split coin
        
        Args:
            owner_address: Owner address
            coin_type: Coin type
            amount: Split amount
            txn: Transaction object
            
        Returns:
            Dict[str, Any]: Split coin info
        """
        # Get coin list
        coins = await self.client.execute_query_node(
            with_node=qn.GetCoins(
                owner=owner_address,
                coin_type=coin_type
            )
        )
        coins_data = handle_result(coins)
        
        if not coins_data or len(coins_data.data) == 0:
            raise ValueError(f"no {coin_type} coins available")
        
        # Filter out enough coins
        selected_coins = []
        total_amount = 0
        for coin in coins_data.data:
            selected_coins.append(coin.coin_object_id)
            total_amount += int(coin.balance)
            if total_amount >= amount:
                break

        if not selected_coins or total_amount < amount:
            raise ValueError(
                f"{coin_type} balance is not enough, current total balance:{total_amount}"
            )

        # Merge coins (if selected coins are more than 1)
        if len(selected_coins) > 1:
            await txn.merge_coins(
                merge_to=selected_coins[0],
                merge_from=selected_coins[1:],
            )

        # Split out the specified amount of coins
        split_result = await txn.split_coin(
            coin=selected_coins[0],
            amounts=[amount]
        )
        return split_result

    async def remove_liquidity(
        self,
        pool_id: str,
        coin_x_type: str,
        coin_y_type: str,
        lp_amount: int,
    ) -> Dict[str, Any]:
        """Remove liquidity from a pool.
        
        This method allows users to withdraw their liquidity from a pool by burning
        their LP tokens. The user will receive both tokens in the pair in proportion
        to their share of the pool.
        
        Args:
            pool_id (str): The ID of the pool to remove liquidity from.
            coin_x_type (str): The type of the first token in the pair.
            coin_y_type (str): The type of the second token in the pair.
            lp_amount (int): The amount of LP tokens to burn.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - tx_id (str): The transaction ID if successful, empty string if failed
                - status (bool): True if the transaction was successful, False otherwise
                - error (str, optional): Error message if the transaction failed
        
        Raises:
            ValueError: If the LP amount is invalid or pool information cannot be retrieved
        """
        try:
            if lp_amount <= 0:
                raise ValueError("Amount must be greater than 0")
            
            coin_x_type, coin_y_type, lp_type = sort_and_get_lp_type(
                CONTRACT_CONSTANTS[self.network].package_id,
                coin_x_type,
                coin_y_type
            )

            # Get pool info
            pool = await self.get_pool(pool_id)
            if not pool:
                raise ValueError("Failed to get pool info")

            # Build transaction block
            txn = SuiTransaction(client=self.client)
            
            # Split LP coin
            split_lp_coin = await self._split_coin(
                self.client.config.active_address,
                lp_type,
                lp_amount,
                txn
            )

            # Call contract to remove liquidity
            await txn.move_call(
                target=f"{CONTRACT_CONSTANTS[self.network].package_id}::router::remove_liquidity",
                arguments=[
                    CONTRACT_CONSTANTS[self.network].version_id,
                    CONTRACT_CONSTANTS[self.network].global_id,
                    pool_id,
                    split_lp_coin
                ],
                type_arguments=[coin_x_type, coin_y_type]
            )

            # Execute transaction
            tx_data = await txn.build_and_sign()
            tx_result = await txn.client.execute_query_node(
                with_node=qn.ExecuteTransaction(**tx_data)
            )
            tx_result = handle_result(tx_result)

            return {
                "tx_id": tx_result.digest,
                "status": True
            }

        except Exception as e:
            return {
                "tx_id": "",
                "status": False,
                "error": str(e)
            }

    async def swap_exact_in(
        self,
        pool_id: str,
        coin_in_type: str,
        coin_out_type: str,
        amount_in: int,
        slippage: float = DEFAULT_SLIPPAGE,
    ) -> Dict[str, Any]:
        """Swap an exact amount of input tokens for output tokens.
        
        This method performs a swap where the user specifies the exact amount of input
        tokens they want to spend. The output amount is calculated based on the pool's
        current price and liquidity.
        
        Args:
            pool_id (str): The ID of the pool to perform the swap in.
            coin_in_type (str): The type of the input token.
            coin_out_type (str): The type of the output token.
            amount_in (int): The exact amount of input tokens to spend.
            slippage (float, optional): The maximum acceptable slippage in percentage.
                                      Defaults to DEFAULT_SLIPPAGE (0.5%).
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - tx_id (str): The transaction ID if successful, empty string if failed
                - status (bool): True if the transaction was successful, False otherwise
                - error (str, optional): Error message if the transaction failed
        
        Raises:
            ValueError: If the input amount is invalid or slippage is out of range
        """
        try:
            if amount_in <= 0:
                raise ValueError("Amount must be greater than 0")
            if slippage >= 1.0 or slippage < 0.0:
                raise ValueError("Slippage must be less than 100% and greater than 0%")

            # Get pool info
            pool = await self.get_pool(pool_id)
            if not pool:
                raise ValueError("Failed to get pool info")
            
            pool_x_type, pool_y_type = sort_type(coin_in_type, coin_out_type)

            # Build transaction block
            txn = SuiTransaction(client=self.client)
            
            # Split X coin
            split_coin_in = await self._split_coin(
                self.client.config.active_address,
                coin_in_type,
                amount_in,
                txn
            )

            if coin_in_type == pool_x_type:
                expected_amount_out = get_amount_out(
                    Decimal(str(pool.fee_rate.value)),
                    Decimal(str(amount_in)),
                    Decimal(str(pool.bal_x.value)),
                    Decimal(str(pool.bal_y.value))
                )
                target = f"{CONTRACT_CONSTANTS[self.network].package_id}::router::swap_exact_x_to_y"
            else:
                expected_amount_out = get_amount_out(
                    Decimal(str(pool.fee_rate.value)),
                    Decimal(str(amount_in)),
                    Decimal(str(pool.bal_y.value)),
                    Decimal(str(pool.bal_x.value))
                )
                target = f"{CONTRACT_CONSTANTS[self.network].package_id}::router::swap_exact_y_to_x"

            # Calculate minimum output amount (considering slippage)
            min_amount_out = int(expected_amount_out * Decimal(1.0 - slippage))

            # Call contract to swap
            await txn.move_call(
                target=target,
                arguments=[
                    CONTRACT_CONSTANTS[self.network].version_id,
                    CONTRACT_CONSTANTS[self.network].global_id,
                    pool_id,
                    split_coin_in,
                    min_amount_out
                ],
                type_arguments=[pool_x_type, pool_y_type]
            )

            # Execute transaction
            tx_data = await txn.build_and_sign()
            tx_result = await txn.client.execute_query_node(
                with_node=qn.ExecuteTransaction(**tx_data)
            )
            tx_result = handle_result(tx_result)

            return {
                "tx_id": tx_result.digest,
                "status": True
            }

        except Exception as e:
            return {
                "tx_id": "",
                "status": False,
                "error": str(e)
            }

    async def swap_exact_out(
        self,
        pool_id: str,
        coin_in_type: str,
        coin_out_type: str,
        amount_out: int,
        slippage: float = DEFAULT_SLIPPAGE,
    ) -> Dict[str, Any]:
        """Swap input tokens for an exact amount of output tokens.
        
        This method performs a swap where the user specifies the exact amount of output
        tokens they want to receive. The required input amount is calculated based on
        the pool's current price and liquidity.
        
        Args:
            pool_id (str): The ID of the pool to perform the swap in.
            coin_in_type (str): The type of the input token.
            coin_out_type (str): The type of the output token.
            amount_out (int): The exact amount of output tokens to receive.
            slippage (float, optional): The maximum acceptable slippage in percentage.
                                      Defaults to DEFAULT_SLIPPAGE (0.5%).
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - tx_id (str): The transaction ID if successful, empty string if failed
                - status (bool): True if the transaction was successful, False otherwise
                - error (str, optional): Error message if the transaction failed
        
        Raises:
            ValueError: If the output amount is invalid or slippage is out of range
        """
        try:
            if amount_out <= 0:
                raise ValueError("Amount must be greater than 0")
            if slippage >= 1.0 or slippage < 0.0:
                raise ValueError("Slippage must be less than 100% and greater than 0%")

            # Get pool info
            pool = await self.get_pool(pool_id)
            if not pool:
                raise ValueError("Failed to get pool info")

            pool_x_type, pool_y_type = sort_type(coin_in_type, coin_out_type)
            if pool_x_type == coin_in_type:
                balance_x = pool.bal_x.value
                balance_y = pool.bal_y.value
                target = f"{CONTRACT_CONSTANTS[self.network].package_id}::router::swap_x_to_exact_y"
            else:
                balance_x = pool.bal_y.value
                balance_y = pool.bal_x.value
                target = f"{CONTRACT_CONSTANTS[self.network].package_id}::router::swap_y_to_exact_x"

            expected_amount_in = get_amount_in(
                Decimal(str(pool.fee_rate.value)),
                Decimal(str(amount_out)),
                Decimal(str(balance_x)),
                Decimal(str(balance_y))
            )
            max_amount_in = int(expected_amount_in / Decimal(1.0 - slippage))

            # Build transaction block
            txn = SuiTransaction(client=self.client)
            
            # Split X coin
            split_coin_in = await self._split_coin(
                self.client.config.active_address,
                coin_in_type,
                max_amount_in,
                txn
            )

            # Call contract to swap
            await txn.move_call(
                target=target,
                arguments=[
                    CONTRACT_CONSTANTS[self.network].version_id,
                    CONTRACT_CONSTANTS[self.network].global_id,
                    pool_id,
                    split_coin_in,
                    amount_out
                ],
                type_arguments=[pool_x_type, pool_y_type]
            )

            # Execute transaction
            tx_data = await txn.build_and_sign()
            tx_result = await txn.client.execute_query_node(
                with_node=qn.ExecuteTransaction(**tx_data)
            )
            tx_result = handle_result(tx_result)

            return {
                "tx_id": tx_result.digest,
                "status": True
            }

        except Exception as e:
            return {
                "tx_id": "",
                "status": False,
                "error": str(e)
            }