from fastapi import APIRouter,Form,UploadFile,Depends,HTTPException,status
from sqlalchemy.orm import Session 
from database import *
from models.model import *
from models.schema import *
from security import *
import uuid
from config import settings

import cloudinary
from cloudinary import CloudinaryImage
import cloudinary.uploader
import cloudinary.api

import json
#config = cloudinary.config(secure=True)


cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)


product_router=APIRouter(prefix='/products',tags=['products'])


@product_router.post('/new',response_model=ProductRead)
async def create_product(
    file:UploadFile,
    title:str=Form(...),
    description:str=Form(...),
    db:Session=Depends(connect),
    user:User=Depends(RoleChecker(['admin']))
):

    file_bytes=await file.read()  
    upload_result=cloudinary.uploader.upload(file_bytes,
         public_id=str(uuid.uuid4()),
         unique_filename = False, overwrite=True)
    srcURL = upload_result['secure_url']
    product=Product(
        title=title,
        image=srcURL,
        description=description,
        user_id=user.id
    )

    db.add(product)
    db.commit()
    db.refresh(product)
    return product 


@product_router.get('/all',response_model=list[ProductRead])
async def get_all_products(
    db:Session=Depends(connect),
    user:User=Depends(get_current_active_user)
):
    products=db.query(Product).all()
    return products


@product_router.get('/{id}',response_model=ProductRead)
async def get_product(
    id:int,
    db:Session=Depends(connect),
    user:User=Depends(get_current_active_user)
):
    product=db.query(Product).filter(Product.id==id).first()
    if not product:
        raise HTTPException(detail='product does not exist',
                            status_code=status.HTTP_404_NOT_FOUND)
    
    return product 


@product_router.delete('/{id}')
async def delete_product(
    id:int,
    db:Session=Depends(connect),
    user:User=Depends(RoleChecker(['admin']))
    ):
    product=db.query(Product).filter(Product.id==id).first()
    if not product:
        raise HTTPException(
            detail='product not found',
            status_code=status.HTTP_404_NOT_FOUND
        )
    db.delete(product)
    db.commit()
    return {'message':'product deleted successfully'}
    

