class PoolNotFound(Exception):
    """Exception raised when a liquidity pool cannot be found.
    
    This exception is raised when attempting to interact with a pool that does not exist
    or cannot be found in the pool registry.
    
    Attributes:
        coin_x_type (str): The type of the first token in the pair
        coin_y_type (str): The type of the second token in the pair
        message (str): The error message explaining why the pool was not found
    """
    
    def __init__(self, coin_x_type: str, coin_y_type: str, message: str = "Pool not found"):
        self.coin_x_type = coin_x_type
        self.coin_y_type = coin_y_type
        self.message = f"{message} for pair {coin_x_type}/{coin_y_type}"
        super().__init__(self.message)

class UnreachableException(Exception):
    """Exception raised when a code path is unreachable.
    
    This exception is raised when a code path is unexpectedly reached, indicating
    a logical error or unexpected code execution in the code.

    Attributes:
        message (str): The error message explaining why the code path is unreachable
    """

    def __init__(self, message: str = "Unreachable code path"):
        self.message = message
        super().__init__(self.message)