from fastapi import APIRouter,UploadFile,Query,File,Form,UploadFile,Depends,HTTPException,status
from sqlalchemy.orm import Session 
from database import *
from models.model import *
from models.schema import *
from security import *
from payment import *
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


bonus_router=APIRouter(prefix='/bonuses',tags=['bonuses'])


#we are claiming a bonus on only what we have purchased  so we enter the id of what we purchased right
#that is how the logic flows
@bonus_router.post('/claim',response_model=BonusRead)
async def claim_bonus(
    id:int=Query(...),
    file:UploadFile=File(...),
    title:str=Form(...),
    amount:float=Form(...),
    
    db:Session=Depends(connect),
    current_user:User=Depends(get_current_user)

):
    
    file_bytes=await file.read()  
    upload_result=cloudinary.uploader.upload(file_bytes,
         public_id=str(uuid.uuid4()),
         unique_filename = False, overwrite=True)
    image = upload_result['secure_url']
    purchase = db.query(Purchase).filter(Purchase.id == id).first()
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
        amount=amount,
        title=title,
        image=image,
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
            disburse_payments(
                phone_number=bonus.customer.phone_number,amount=10 )
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




@bonus_router.get('/all',response_model=list[BonusRead])
async def get_all_bonuses(
    db:Session=Depends(connect)
):
    bonuses=db.query(Bonus).all()
    return bonuses


@bonus_router.get('/my/bonuses',response_model=list[BonusRead])
async def get_my_bonuses(
    user:User=Depends(RoleChecker(['customer'])),
    db:Session=Depends(connect)):
    bonuses=db.query(Bonus).filter(Bonus.user_id==user.id).all()
    return bonuses 


@bonus_router.get('/bonus/status',response_model=list[BonusRead])
async def get_bonuses_state(
    bonus_state:str=Query(...),
    db:Session=Depends(connect),
    user:User=Depends(get_current_active_user)
):
    bonuses=db.query(Bonus).filter(Bonus.status==bonus_state , Bonus.user_id==user.id).all()
    return bonuses

@bonus_router.delete('/bonus/{id}')
async def delete_bonus(
    id:int,
    user:User=Depends(RoleChecker(['admin'])),
    db:Session=Depends(connect)
):
    bonuse=db.query(Bonus).filter(Bonus.id==id).first()
    if not bonuse:
        raise HTTPException(
            detail='bonus does not exist',
            status_code=405
        )
    db.delete(bonuse)
    db.commit()
    return {'message':'bonuse deleted successfully'}
