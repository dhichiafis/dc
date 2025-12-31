from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from models.model import Purchase, Product, User
from models.schema import PurchaseCreate, PurchaseRead
from database import *
from security import get_current_user

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

    #  Validate seller exists
    seller = db.query(User).filter(User.id == purchase_in.seller_id).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")

    #  Create purchase record
    purchase = Purchase(
        product_id=purchase_in.product_id,
        customer_id=current_user.id,
        seller_id=purchase_in.seller_id,
        created_at=datetime.now()
    )

    db.add(purchase)
    db.commit()
    db.refresh(purchase)

    return purchase
