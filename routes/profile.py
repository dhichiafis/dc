from fastapi import APIRouter,Depends,HTTPException,status,BackgroundTasks
from models.model import *
from models.schema import *
from sqlalchemy.orm import Session 
from security import *
from jose import jwt,JWTError
from database import *
#from email_utils import send_email
from typing import Annotated


profiles_router=APIRouter(tags=['profiles'],prefix='/profiles')


@profiles_router.get('/my/profile',response_model=ProfileBase)
async def get_my_profile(
    user:User=Depends(get_current_active_user),
    db:Session=Depends(connect)
):
    profile=user.profile
    if not profile:
        raise HTTPException(
            detail='profile not found',
            status_code=402
        )
    return profile



    

