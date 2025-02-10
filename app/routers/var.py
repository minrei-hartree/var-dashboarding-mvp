import pandas as pd
from fastapi import APIRouter

router = APIRouter()

@router.get('/var/pnl_vectors', tags=['var'])
async def get_pnl_vectors():
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