from pydantic import BaseModel
from dataclasses import dataclass

from pysui.sui.sui_types.scalars import SuiU64


@dataclass
class Pool:
    id: str
    bal_x: SuiU64
    bal_y: SuiU64
    fee_bal_x: SuiU64
    fee_bal_y: SuiU64
    lp_supply: SuiU64
    fee_rate: SuiU64
    min_liquidity: SuiU64

    @staticmethod
    def from_gql_response(response: dict) -> "Pool":
        return Pool(
            id=response["id"],
            bal_x=SuiU64(response["bal_x"]["value"]),
            bal_y=SuiU64(response["bal_y"]["value"]),
            fee_bal_x=SuiU64(response["fee_bal_x"]["value"]),
            fee_bal_y=SuiU64(response["fee_bal_y"]["value"]),
            lp_supply=SuiU64(response["lp_supply"]["value"]),
            fee_rate=SuiU64(response["fee_rate"]),
            min_liquidity=SuiU64(response["min_liquidity"]["value"])
        )
