import pandas as pd
from fastapi import APIRouter
from ..minrei_lib import Core

router = APIRouter()

@router.get('/var/pnl_vectors', tags=['var'])
async def get_pnl_vectors(trader: str):
    df = Core.generate_pnl_vectors(trader)
    return df.to_dict(orient='records')

@router.get('/var/pnl_vectors_test', tags=['var'])
async def get_pnl_vectors_test():
    df = pd.read_csv("./sample_pnl_vectors.csv")
    return df.to_dict(orient='records')

@router.get('/var/test', tags=['var'])
async def get_data():
    df = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "value": [10, 20, 30]
    })
    return df.to_dict(orient="records")