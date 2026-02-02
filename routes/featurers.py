from fastapi import APIRouter,Form,UploadFile,Depends,HTTPException,status
from sqlalchemy.orm import Session 
from database import *
from models.model import *
from models.schema import *
from security import *


feature_router=APIRouter(tags=['features'],prefix='/features')

@feature_router.post('/new',response_model=FeatureRead)
async def create_feature(
        nf:FeatureCreate,
        id:int,
        user:User=Depends(RoleChecker(['admin'])),
        db:Session=Depends(connect)):
    product=db.query(Product).filter(Product.id==id).first()
    if not product:
        raise HTTPException(
            status_code='405',
            detail='product not found'
        )
    
    feature=Feature(name=nf.name)
    feature.product_id=product.id 
    db.add(feature)
    db.commit()
    db.refresh(feature)
    return feature 

@feature_router.get('/all/{id}',response_model=List[FeatureRead])
async def get_product_features(
    id:int,
    user:User=Depends(get_current_active_user),
    db:Session=Depends(connect)):
    
    features=db.query(Feature).filter(Feature.product_id==id).all()
    if not features:
        raise HTTPException(
            detail='features are not found for this product',
            status_code=404
        )
    return features



@feature_router.get('/all',response_model=List[FeatureRead])
async def get_all_features(
    user:User=Depends(get_current_active_user),
    db:Session=Depends(connect)):
    features=db.query(Feature).all()
    return features


@feature_router.delete('/{id}')
async def delete_feature(id:int,db:Session=Depends(connect)):
    feature=db.query(Feature).first()
    if not feature:
        raise HTTPException(
            detail='feature not found',
            status_code=405
        )
    db.commit()
    return {'message':'feature deleted successfully'}