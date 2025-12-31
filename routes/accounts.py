from fastapi import APIRouter,Depends,HTTPException

from sqlalchemy.orm import Session
from database import *
from models.model import *
from models.schema import *
from security import *
from typing import List 


accounts_router=APIRouter(
    tags=['accounts'],prefix='/accounts'
)


@accounts_router.get('/all',response_model=List[AccountBase])
async def get_all_accounts(db:Session=Depends(connect),
    user:User=Depends(RoleChecker(['admin']))
        ):
    accounts=db.query(Account).all()
    return accounts


@accounts_router.get('/{id}',response_model=AccountBase)
async def get_account(id:int,
    user:User=Depends(RoleChecker(['admin'])),
    db:Session=Depends(connect)
    ):
    account=db.query(Account).filter(Account.id==id).first()
    return account 