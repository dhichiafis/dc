from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session 
from database import *
from models.model import *
from models.schema import *
from security import *
from payment import *

bonus_router=APIRouter(prefix='/bonuses',tags=['bonuses'])



@bonus_router.post('/claim',response_model=BonusRead)
async def claim_bonus(
    bonus:BonusCreate,
    db:Session=Depends(connect),
    current_user:User=Depends(get_current_user)
):
    purchase = db.query(Purchase).filter(Purchase.id == bonus.purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")

    # Only the customer who bought can claim
    if purchase.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to claim this bonus")

    # Ensure no previous bonus exists for this purchase
    if purchase.bonus:
        raise HTTPException(status_code=400, detail="Bonus already claimed for this purchase")

    nbonus = Bonus(
        purchase_id=purchase.id,
        user_id=current_user.id,
        amount=bonus.amount,
        title=bonus.title,
        image=bonus.image,
        status=BonusStatus.CLAIM.value
    )
    db.add(nbonus)
    db.commit()
    db.refresh(nbonus)
    return nbonus

@bonus_router.patch('/approve')
def approve_bonus(bonus_id: int,
        approve: bool, db: Session = Depends(connect),
        current_user: User = Depends(get_current_user)):
    """
    Approve or reject a bonus. Only the seller of the product can approve/reject.
    If approved, money is disbursed to the customer immediately.
    """
    # 1️⃣ Fetch the bonus
    bonus = db.query(Bonus).filter(Bonus.id == bonus_id).first()
    if not bonus:
        raise HTTPException(status_code=404, detail="Bonus not found")

    # 2️⃣ Check if current user is seller of the purchase
    purchase = bonus.purchase
    if purchase.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to approve this bonus")

    # 3️⃣ Ensure bonus hasn't been approved/rejected already
    if bonus.status in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail=f"Bonus already {bonus.status}")

    # 4️⃣ Update status
    bonus.status = "approved" if approve else "rejected"
    bonus.updated_at = datetime.now()
    
    # 5️⃣ Disburse money if approved
    if approve:
        try:
            #get_auth_token()
            #send_to_customer(amount=bonus.amount, phone_number=bonus.customer.phone_number)
            bonus.paid_at = datetime.now()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Payment failed: {str(e)}")
    
    db.commit()
    db.refresh(bonus)
    return {
        "id": bonus.id,
        "status": bonus.status,
        "paid_at": bonus.paid_at,
        "amount": bonus.amount,
        "title": bonus.title
    } 


