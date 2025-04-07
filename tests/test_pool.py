import pytest
from dipcoin.types import Pool
from dipcoin.math import U64_MAX

def test_pool_creation():
    pool = Pool(
        id="test_pool",
        bal_x=1000,
        bal_y=2000,
        fee_bal_x=10,
        fee_bal_y=20,
        lp_supply=100,
        fee_rate=30,
        min_liquidity=1
    )
    
    assert pool.id == "test_pool"
    assert pool.bal_x == 1000
    assert pool.bal_y == 2000
    assert pool.fee_bal_x == 10
    assert pool.fee_bal_y == 20
    assert pool.lp_supply == 100
    assert pool.fee_rate == 30
    assert pool.min_liquidity == 1

def test_pool_from_gql_response():
    gql_response = {
        "id": "test_pool",
        "bal_x": {"value": "1000"},
        "bal_y": {"value": "2000"},
        "fee_bal_x": {"value": "10"},
        "fee_bal_y": {"value": "20"},
        "lp_supply": {"value": "100"},
        "fee_rate": "30",
        "min_liquidity": {"value": "1"}
    }
    
    pool = Pool.from_gql_response(gql_response)
    
    assert pool.id == "test_pool"
    assert pool.bal_x == 1000
    assert pool.bal_y == 2000
    assert pool.fee_bal_x == 10
    assert pool.fee_bal_y == 20
    assert pool.lp_supply == 100
    assert pool.fee_rate == 30
    assert pool.min_liquidity == 1

def test_pool_validation():
    pool = Pool(
        id="test_pool",
        bal_x=0,
        bal_y=0,
        fee_bal_x=0,
        fee_bal_y=0,
        lp_supply=0,
        fee_rate=0,
        min_liquidity=0
    )
    assert pool.bal_x == 0
    
    pool = Pool(
        id="test_pool",
        bal_x=U64_MAX,
        bal_y=U64_MAX,
        fee_bal_x=U64_MAX,
        fee_bal_y=U64_MAX,
        lp_supply=U64_MAX,
        fee_rate=U64_MAX,
        min_liquidity=U64_MAX
    )
    assert pool.bal_x == U64_MAX

def test_pool_validation_errors():
    with pytest.raises(ValueError):
        Pool(
            id="test_pool",
            bal_x=-1,
            bal_y=0,
            fee_bal_x=0,
            fee_bal_y=0,
            lp_supply=0,
            fee_rate=0,
            min_liquidity=0
        )
    
    with pytest.raises(ValueError):
        Pool(
            id="test_pool",
            bal_x=U64_MAX + 1,
            bal_y=0,
            fee_bal_x=0,
            fee_bal_y=0,
            lp_supply=0,
            fee_rate=0,
            min_liquidity=0
        )
    
    with pytest.raises(ValueError):
        Pool(
            id="test_pool",
            bal_x=1.5,
            bal_y=0,
            fee_bal_x=0,
            fee_bal_y=0,
            lp_supply=0,
            fee_rate=0,
            min_liquidity=0
        ) 