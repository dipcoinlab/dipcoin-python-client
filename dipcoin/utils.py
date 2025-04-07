from canoser import StrT

def compare_u8_vector(left: bytes, right: bytes) -> bool:
    """Compare two byte arrays
    
    Args:
        left: First byte array
        right: Second byte array
        
    Returns:
        bool: Returns True if left is less than right, otherwise returns False
    """
    left_length = len(left)
    right_length = len(right)
    
    for idx in range(min(left_length, right_length)):
        if left[idx] < right[idx]:
            return True
        if left[idx] > right[idx]:
            return False
            
    if left_length < right_length:
        return True
    if left_length > right_length:
        return False
    return False

def is_type_x_smaller_than_type_y(type_x: str, type_y: str) -> bool:
    """Compare the size of two strings using BCS serialization.
    
    Args:
        type_x: First string
        type_y: Second string
        
    Returns:
        bool: Returns True if x is less than y, otherwise returns False
    """
    type_x_bytes = StrT.encode(type_x)
    type_y_bytes = StrT.encode(type_y)
    
    return compare_u8_vector(type_x_bytes, type_y_bytes)

def sort_type(coin_x_type: str, coin_y_type: str) -> list[str, str]:
    """Sort token types"""
    if is_type_x_smaller_than_type_y(coin_x_type, coin_y_type):
        return [coin_x_type, coin_y_type]
    else:
        return [coin_y_type, coin_x_type]

def format_lp_name(coin_x_type: str, coin_y_type: str) -> str:
    """Format LP name"""
    if coin_x_type.startswith('0x'):
        coin_x_type = coin_x_type[2:]
    if coin_y_type.startswith('0x'):
        coin_y_type = coin_y_type[2:]
    if is_type_x_smaller_than_type_y(coin_x_type, coin_y_type):
        return f"LP-{coin_x_type}-{coin_y_type}"
    else:
        return f"LP-{coin_y_type}-{coin_x_type}"
    
def sort_and_get_lp_type(package_id: str, type_x: str, type_y: str) -> list[str, str, str]:
    [new_type_x, new_type_y] = sort_type(type_x, type_y)
    lp_type = f"{package_id}::manage::LP<{new_type_x}, {new_type_y}>"
    return [new_type_x, new_type_y, lp_type]
