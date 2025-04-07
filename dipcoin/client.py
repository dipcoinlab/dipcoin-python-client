"""Dipcoin Python SDK"""
from typing import Dict, Any

from pysui import PysuiConfiguration, handle_result, AsyncGqlClient
from pysui.sui.sui_pgql import pgql_query as qn
from pysui.sui.sui_pgql.pgql_types import ObjectReadGQL, NoopGQL
from pysui.sui.sui_pgql.pgql_async_txn import AsyncSuiTransaction as SuiTransaction

from .types import Pool, TransactionResponse
from .utils import format_lp_name, sort_type, sort_and_get_lp_type
from .constants import CONTRACT_CONSTANTS, DEFAULT_SLIPPAGE
from .math import calc_optimal_coin_values, get_amount_out, get_amount_in
from .query import DipCoinQuery
from .exceptions import PoolNotFound, UnreachableException

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
        self.query = DipCoinQuery(network)
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
                raise UnreachableException(f"Unknown error: {res}")
        elif isinstance(res, NoopGQL):
            return None
        else:
            raise UnreachableException(f"Unknown error: {res}")
        
    async def get_pool_id(self, coin_x_type: str, coin_y_type: str) -> str | None:
        """Get the pool ID for a given pair of tokens.
        
        Args:
            coin_x_type (str): The type of the first token in the pair.
            coin_y_type (str): The type of the second token in the pair.
            
        Returns:
            str | None: The pool ID if found, None if no pool exists for the given pair.
        """
        return await self.query.get_pool_id(coin_x_type, coin_y_type)

    async def add_liquidity(
        self,
        coin_x_type: str,
        coin_y_type: str,
        coin_x_amount: int,
        coin_y_amount: int,
        slippage: float = DEFAULT_SLIPPAGE,
    ) -> TransactionResponse:
        """Add liquidity to a pool.
        
        This method allows users to provide liquidity to a pool by depositing both tokens
        in the pair. The amounts are automatically adjusted to maintain the pool's price ratio.
        
        Args:
            coin_x_type (str): The type of the first token.
            coin_y_type (str): The type of the second token.
            coin_x_amount (int): The amount of the first token to deposit.
            coin_y_amount (int): The amount of the second token to deposit.
            slippage (float, optional): The maximum acceptable slippage in percentage.
                                      Defaults to DEFAULT_SLIPPAGE (0.5%).
        
        Returns:
            TransactionResponse: A TransactionResponse object containing the transaction digest and status
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
            pool_id = await self.query.get_pool_id(coin_x_type, coin_y_type)
            if not pool_id:
                raise PoolNotFound(coin_x_type, coin_y_type)
            pool = await self.get_pool(pool_id)
            if not pool:
                raise PoolNotFound(coin_x_type, coin_y_type)

            # Calculate optimal amounts
            coin_x_desired, coin_y_desired = calc_optimal_coin_values(
                coin_x_amount,
                coin_y_amount,
                pool.bal_x,
                pool.bal_y,
            )
            # Calculate minimum accepted amounts (considering slippage)
            coin_x_min = int(coin_x_desired * (1.0 - slippage))
            coin_y_min = int(coin_y_desired * (1.0 - slippage))

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
            final_result = await self._execute_and_wait(txn)
            # TODO: check effects
            # if final_result.is_ok():
            #     res = handle_result(final_result)
            #     print(type(res.effects))
            #     print(res.effects['balanceChanges']['nodes'])
            # elif final_result.is_err():
            #     print(final_result.result_string)
            # else:
            #     raise UnreachableException(f"Unknown error: {final_result}")

            return final_result

        except Exception as e:
            return TransactionResponse(
                digest="",
                status=False,
                error=str(e)
            )

    async def remove_liquidity(
        self,
        coin_x_type: str,
        coin_y_type: str,
        lp_amount: int,
    ) -> TransactionResponse:
        """Remove liquidity from a pool.
        
        This method allows users to withdraw their liquidity from a pool by burning
        their LP tokens. The user will receive both tokens in the pair in proportion
        to their share of the pool.
        
        Args:
            coin_x_type (str): The type of the first token in the pair.
            coin_y_type (str): The type of the second token in the pair.
            lp_amount (int): The amount of LP tokens to burn.
        
        Returns:
            TransactionResponse: A TransactionResponse object containing the transaction digest and status
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
            pool_id = await self.query.get_pool_id(coin_x_type, coin_y_type)
            if not pool_id:
                raise PoolNotFound(coin_x_type, coin_y_type)
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
            return await self._execute_and_wait(txn)

        except Exception as e:
            return TransactionResponse(
                digest="",
                status=False,
                error=str(e)
            )

    async def swap_exact_in(
        self,
        coin_in_type: str,
        coin_out_type: str,
        amount_in: int,
        slippage: float = DEFAULT_SLIPPAGE,
    ) -> TransactionResponse:
        """Swap an exact amount of input tokens for output tokens.
        
        This method performs a swap where the user specifies the exact amount of input
        tokens they want to spend. The output amount is calculated based on the pool's
        current price and liquidity.
        
        Args:
            coin_in_type (str): The type of the input token.
            coin_out_type (str): The type of the output token.
            amount_in (int): The exact amount of input tokens to spend.
            slippage (float, optional): The maximum acceptable slippage in percentage.
                                      Defaults to DEFAULT_SLIPPAGE (0.5%).
        
        Returns:
            TransactionResponse: A TransactionResponse object containing the transaction digest and status
        """
        try:
            if amount_in <= 0:
                raise ValueError("Amount must be greater than 0")
            if slippage >= 1.0 or slippage < 0.0:
                raise ValueError("Slippage must be less than 100% and greater than 0%")
            
            pool_id = await self.query.get_pool_id(coin_in_type, coin_out_type)
            if not pool_id:
                raise PoolNotFound(coin_in_type, coin_out_type)

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
                target = f"{CONTRACT_CONSTANTS[self.network].package_id}::router::swap_exact_x_to_y"
                reverse_in = pool.bal_x
                reverse_out = pool.bal_y
            else:
                target = f"{CONTRACT_CONSTANTS[self.network].package_id}::router::swap_exact_y_to_x"
                reverse_in = pool.bal_y
                reverse_out = pool.bal_x

            expected_amount_out = get_amount_out(
                pool.fee_rate,
                amount_in,
                reverse_in,
                reverse_out
            )
            # Calculate minimum output amount (considering slippage)
            min_amount_out = int(expected_amount_out * (1.0 - slippage))

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
            return await self._execute_and_wait(txn)

        except Exception as e:
            return TransactionResponse(
                digest="",
                status=False,
                error=str(e)
            )

    async def swap_exact_out(
        self,
        coin_in_type: str,
        coin_out_type: str,
        amount_out: int,
        slippage: float = DEFAULT_SLIPPAGE,
    ) -> TransactionResponse:
        """Swap input tokens for an exact amount of output tokens.
        
        This method performs a swap where the user specifies the exact amount of output
        tokens they want to receive. The required input amount is calculated based on
        the pool's current price and liquidity.
        
        Args:
            coin_in_type (str): The type of the input token.
            coin_out_type (str): The type of the output token.
            amount_out (int): The exact amount of output tokens to receive.
            slippage (float, optional): The maximum acceptable slippage in percentage.
                                      Defaults to DEFAULT_SLIPPAGE (0.5%).
        
        Returns:
            TransactionResponse: A TransactionResponse object containing the transaction digest and status
        """
        try:
            if amount_out <= 0:
                raise ValueError("Amount must be greater than 0")
            if slippage >= 1.0 or slippage < 0.0:
                raise ValueError(r"Slippage must be less than 100% and greater than 0%")

            # Get pool info
            pool_id = await self.query.get_pool_id(coin_in_type, coin_out_type)
            if not pool_id:
                raise PoolNotFound(coin_in_type, coin_out_type)
            pool = await self.get_pool(pool_id)
            if not pool:
                raise ValueError("Failed to get pool info")

            pool_x_type, pool_y_type = sort_type(coin_in_type, coin_out_type)
            if pool_x_type == coin_in_type:
                reverse_in = pool.bal_x
                reverse_out = pool.bal_y
                target = f"{CONTRACT_CONSTANTS[self.network].package_id}::router::swap_x_to_exact_y"
            else:
                reverse_in = pool.bal_y
                reverse_out = pool.bal_x
                target = f"{CONTRACT_CONSTANTS[self.network].package_id}::router::swap_y_to_exact_x"

            expected_amount_in = get_amount_in(
                pool.fee_rate,
                amount_out,
                reverse_in,
                reverse_out
            )
            max_amount_in = int(expected_amount_in / (1.0 - slippage))

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
            return await self._execute_and_wait(txn)

        except Exception as e:
            return TransactionResponse(
                digest="",
                status=False,
                error=str(e)
            )
        
    async def _execute_and_wait(self, txn: SuiTransaction) -> TransactionResponse:
        """Execute transaction and wait for it to be processed"""
        tx_data = await txn.build_and_sign()
        tx_result = await txn.client.execute_query_node(
            with_node=qn.ExecuteTransaction(**tx_data)
        )
        if tx_result.is_err():
            return TransactionResponse(
                digest="",
                status=False,
                error=tx_result.result_string
            )
        tx_result = handle_result(tx_result)
        assert tx_result.status == 'SUCCESS', tx_result.status
        await self.client.wait_for_transaction(digest=tx_result.digest) # TODO: check effects
        return TransactionResponse(
            digest=tx_result.digest,
            status=True
        )
        

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
