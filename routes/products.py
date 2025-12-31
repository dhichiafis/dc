from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session 
from database import *
from models.model import *
from models.schema import *
from security import *


product_router=APIRouter(prefix='/products',tags=['products'])


@product_router.post('/new',response_model=ProductRead)
async def create_product(
    new_product=ProductCreate,
    db:Session=Depends(connect),
    user:User=Depends(RoleChecker(['admin']))
):
    
    product=Product(
        title=new_product.title,
        description=new_product.description,
        user_id=user.id
    )

    db.add(product)
    db.commit()
    db.refresh(product)
    return product 


@product_router.get('/all',response_model=list[ProductRead])
async def get_all_products(
    db:Session=Depends(connect),
    user:User=Depends(RoleChecker(['admin']))
):
    products=db.query(Product).all()
    return products


@product_router.get('/{id}',response_model=ProductRead)
async def get_product(
    id:int,
    db:Session=Depends(connect)
):
    product=db.query(Product).filter(Product.id==id).first()
    if not product:
        raise HTTPException(detail='product does not exist',
                            status_code=status.HTTP_404_NOT_FOUND)
    
    return product 