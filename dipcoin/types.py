from pydantic import BaseModel, field_validator
from .math import U64_MAX

class Pool(BaseModel):
    """
    Represents a liquidity pool in the DIP protocol.
    
    Attributes:
        id (str): Unique identifier of the pool
        bal_x (int): Balance of token X in the pool (U64)
        bal_y (int): Balance of token Y in the pool (U64)
        fee_bal_x (int): Fee balance of token X (U64)
        fee_bal_y (int): Fee balance of token Y (U64)
        lp_supply (int): Total supply of LP tokens (U64)
        fee_rate (int): Fee rate for swaps (U64)
        min_liquidity (int): Minimum liquidity required (U64)
    """
    id: str
    bal_x: int
    bal_y: int
    fee_bal_x: int
    fee_bal_y: int
    lp_supply: int
    fee_rate: int
    min_liquidity: int

    @field_validator('bal_x', 'bal_y', 'fee_bal_x', 'fee_bal_y', 'lp_supply', 'fee_rate', 'min_liquidity')
    def validate_u64(cls, v):
        """
        Validates that the value is a valid U64 integer.
        
        Args:
            v: The value to validate
            
        Returns:
            The validated value
            
        Raises:
            ValueError: If the value is not a valid U64 integer
        """
        if not isinstance(v, int) or v < 0 or v > U64_MAX:
            raise ValueError(f"Value must be an U64 integer, got {v}")
        return v

    @staticmethod
    def from_gql_response(response: dict) -> "Pool":
        """
        Creates a Pool instance from a GraphQL response.
        
        Args:
            response (dict): The GraphQL response containing pool data
            
        Returns:
            Pool: A new Pool instance
        """
        return Pool(
            id=response["id"],
            bal_x=int(response["bal_x"]["value"]),
            bal_y=int(response["bal_y"]["value"]),
            fee_bal_x=int(response["fee_bal_x"]["value"]),
            fee_bal_y=int(response["fee_bal_y"]["value"]),
            lp_supply=int(response["lp_supply"]["value"]),
            fee_rate=int(response["fee_rate"]),
            min_liquidity=int(response["min_liquidity"]["value"])
        )

class TransactionResponse(BaseModel):
    """
    Represents the response from a blockchain transaction.
    
    Attributes:
        digest (str): The transaction digest/hash
        status (bool): Whether the transaction was successful
        error (str | None): Error message if the transaction failed, None if successful
    """
    digest: str 
    status: bool
    error: str | None = None
    
