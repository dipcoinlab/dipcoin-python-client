from decimal import Decimal

def mul_div(a: Decimal, b: Decimal, c: Decimal) -> Decimal:
    """Multiply a and b, then divide by c."""
    return (a * b) / c

def calc_optimal_coin_values(
    coin_x_desired: Decimal,
    coin_y_desired: Decimal,
    coin_x_reserve: Decimal,
    coin_y_reserve: Decimal
) -> tuple[Decimal, Decimal]:
    """
    Calculate optimal token amounts when adding liquidity
    
    Args:
        coin_x_desired: Expected amount of X coin to add
        coin_y_desired: Expected amount of Y coin to add
        coin_x_reserve: Current X coin reserve in pool
        coin_y_reserve: Current Y coin reserve in pool
        
    Returns:
        tuple[Decimal, Decimal]: Actual amount of (X coin, Y coin) to add
        
    Raises:
        ValueError: When the calculation result exceeds the limit
    """
    if coin_x_reserve == 0 and coin_y_reserve == 0:
        return coin_x_desired, coin_y_desired

    coin_y_returned = mul_div(coin_x_desired, coin_y_reserve, coin_x_reserve)
    if coin_y_returned <= coin_y_desired:
        return coin_x_desired, coin_y_returned
    else:
        coin_x_returned = mul_div(coin_y_desired, coin_x_reserve, coin_y_reserve)
        if coin_x_returned > coin_x_desired:
            raise ValueError("Over limit")
        return coin_x_returned, coin_y_desired


# Constants
FEE_SCALE = Decimal('10000')
MAX_FEE_RATE = Decimal('10000')
U64_MAX = Decimal('18446744073709551615')  # 2^64 - 1

def get_amount_out(fee_rate: Decimal, amount_in: Decimal, reserve_in: Decimal, reserve_out: Decimal) -> Decimal:
    """
    Calculate output amount for a swap
    
    Args:
        fee_rate: Fee rate for the swap
        amount_in: Input amount
        reserve_in: Input token reserve
        reserve_out: Output token reserve
        
    Returns:
        Decimal: Output amount
        
    Raises:
        ValueError: If parameters are invalid
    """
    # If fee_rate = 0, amount_out = y*amount_in/(x + amount_in)
    if fee_rate == 0:
        result = (reserve_out * amount_in) / (reserve_in + amount_in)
        print("getAmountOut result:", int(result))
        return int(result)

    if fee_rate > MAX_FEE_RATE:
        raise ValueError("Invalid fee rate")
    if amount_in == 0:
        raise ValueError("Zero amount")
    if reserve_in == 0 or reserve_out == 0:
        raise ValueError("Reserves empty")

    fee_multiplier = FEE_SCALE - fee_rate
    coin_in_val_after_fees = amount_in * fee_multiplier
    new_reserve_in = reserve_in * FEE_SCALE + coin_in_val_after_fees

    numerator = coin_in_val_after_fees * reserve_out
    amount_out = int(numerator / new_reserve_in)

    if amount_out > U64_MAX:
        raise ValueError("U64 overflow")
    return amount_out

def get_amount_in(fee_rate: Decimal, amount_out: Decimal, reserve_in: Decimal, reserve_out: Decimal) -> Decimal:
    """
    Calculate input amount for a swap
    
    Args:
        fee_rate: Fee rate for the swap
        amount_out: Desired output amount
        reserve_in: Input token reserve
        reserve_out: Output token reserve
        
    Returns:
        Decimal: Required input amount
        
    Raises:
        ValueError: If parameters are invalid
    """
    if fee_rate > MAX_FEE_RATE:
        raise ValueError("Invalid fee rate")
    if amount_out == 0:
        raise ValueError("Zero amount")
    if reserve_in == 0 or reserve_out == 0:
        raise ValueError("Reserves empty")

    fee_multiplier = FEE_SCALE - fee_rate
    numerator = reserve_in * amount_out * FEE_SCALE
    denominator = (reserve_out - amount_out) * fee_multiplier
    amount_in = int(numerator / denominator) + 1

    if amount_in > U64_MAX:
        raise ValueError("U64 overflow")
    return amount_in 