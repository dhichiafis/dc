from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from models.model import Purchase, Product, User
from models.schema import PurchaseCreate, PurchaseRead
from database import *
from security import get_current_user
from security import *
purchase_router = APIRouter(prefix="/purchases", tags=["Purchases"])

@purchase_router.post("/", response_model=PurchaseRead)
def create_purchase(
    purchase_in: PurchaseCreate, 
    db: Session = Depends(connect), 
    current_user: User = Depends(get_current_user)):
    """
    Create a purchase record.
    - current_user is assumed to be the buyer (customer)
    - seller_id must be provided
    """
    # 
    product = db.query(Product).filter(Product.id == purchase_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    # the buyer must have a manager

    if not current_user.managed_by:
        raise HTTPException(
            status_code=400,
            detail="You must be assigned to a manager to make a purchase"
        )

    seller = current_user.managed_by.manager
    #  Validate seller exists
    
     # 3. Bank isolation
    if seller.bank_id != current_user.bank_id:
        raise HTTPException(
            status_code=403,
            detail="Seller belongs to a different bank"
        )
    #  Create purchase record
    purchase = Purchase(
        product_id=purchase_in.product_id,
        customer_id=current_user.id,
        seller_id=seller.id,
        created_at=datetime.now()
    )

    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    return purchase


@purchase_router.get('/my/purchases',response_model=list[PurchaseRead])
async def get_my_purchases(
    db:Session=Depends(connect),
    user:User=Depends(RoleChecker(['customer']))
):
    purchases=db.query(Purchase).filter(Purchase.customer_id==user.id).all()
    return purchases



@purchase_router.get("/all")
async def get_all_purchases(
    db:Session=Depends(connect)
   ,user:User=Depends(RoleChecker(['admin'])) 
    ):
    purchases=db.query(Purchase).all()
    return purchases

@purchase_router.delete('/{id}')
async def delete_purchase(
    id:int,
    db:Session=Depends(connect)):
    purchase=db.query(Purchase).filter(Purchase.id==id).first()
    if not purchase:
        raise HTTPException(
            detail='purchase is not found',
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    db.delete(purchase)
    db.commit()
    return {'message':'purchase successfully deleted'}