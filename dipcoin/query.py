import httpx
from typing import Dict, Any
from pysui.sui.sui_common.async_funcs import AsyncLRU

from .utils import format_lp_name
from .constants import NODE_RPC, CONTRACT_CONSTANTS
from .exceptions import UnreachableException

async def get_dynamic_field_object(
    parent_object_id: str,
    field_type: str,
    field_value: str,
    rpc_url: str,
) -> Dict[str, Any]:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "suix_getDynamicFieldObject",
        "params": [
            parent_object_id,
            {
                "type": field_type,
                "value": field_value
            }
        ]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(rpc_url, json=payload)
        response.raise_for_status()
        return response.json()

class DipCoinQuery:
    def __init__(self, network: str):
        self.rpc_url = NODE_RPC[network]
        self.network = network
        self.pool_registry_table_id = CONTRACT_CONSTANTS[network].pool_registry_table_id

    @AsyncLRU(maxsize=1024)
    async def get_pool_id(self, coin_x_type: str, coin_y_type: str) -> str | None:
        """Get the pool ID for a given pair of tokens.
        
        Args:
            coin_x_type (str): The type of the first token in the pair.
            coin_y_type (str): The type of the second token in the pair.
        """
        table_id = self.pool_registry_table_id

        lp_name = format_lp_name(coin_x_type, coin_y_type)
        field_type = "0x1::string::String"
        field_value = lp_name

        resp = await get_dynamic_field_object(table_id, field_type, field_value, self.rpc_url)
        result = resp['result']
        if 'data' in result:
            return result['data']['content']['fields']['value']
        elif 'error' in result:
            return None
        else:
            raise UnreachableException()
