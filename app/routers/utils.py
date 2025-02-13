from fastapi import APIRouter
from ..minrei_lib import Database


router = APIRouter()

@router.get('/utils/traders', tags=['utils'])
async def get_traders_list():
    db = Database()
    return db.traders.list_traders()

@router.get('/utils/groups', tags=['utils'])
async def get_groups_list():
    db = Database()
    return db.traders.list_groups()