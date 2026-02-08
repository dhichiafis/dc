from fastapi import APIRouter,Depends,HTTPException,status,BackgroundTasks
from models.model import *
from models.schema import *
from sqlalchemy.orm import Session 
from security import *
from jose import jwt,JWTError
from database import *
from email_utils import send_email
from typing import Annotated
users_router=APIRouter(tags=['users'],prefix='/users')


@users_router.post('/token')
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm=Depends(),
    db:Session=Depends(connect)
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username,}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")



@users_router.post('/admin',response_model=UserBase)
async def create_admin(
    bank_admin:BankAdmin,
    
    db:Session=Depends(connect)
):
    bank_exist=db.query(Bank).filter(Bank.name==bank_admin.bank_name).first()
    if bank_exist:
        raise HTTPException(
            detail='bank already created',
            status_code=400
        )
    bank=Bank(name=bank_admin.bank_name)
    db.add(bank)
    db.flush()
    role_exist=db.query(Role).filter(Role.name=='admin').first()
    if not role_exist:
        raise HTTPException(
            detail='role is not created yet',
            status_code=402
        )
    user_exist=db.query(User).filter(User.username==bank_admin.username).first()
    if user_exist:
        raise HTTPException(
            detail='user with username already exist',
            status_code=401)
    
    password=get_password_hash(bank_admin.password)
    user=User(username=bank_admin.username,
            phone_number=bank_admin.phone_number,
            email=bank_admin.email,
            password=password,bank_id=bank.id,role_id=role_exist.id)
    db.add(user)
    db.commit()
    db.refresh(user)
    profile=Profile(
        status='customer',
        funded_amount=0.0,
        funding_status="pending",
    )
    profile.user_id=user.id

    db.add(profile)
    db.commit()
    db.refresh(profile)
    wallet=Wallet()
    wallet.user_id=user.id 
    wallet.is_bank=True
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return user


@users_router.post('/new/customer',response_model=UserBase)
async def create_new_customer(
    customer:CustomerCreate,
    background_task:BackgroundTasks,
    db:Session=Depends(connect),
    ma:User=Depends(RoleChecker(['admin','relation manager']))
):
    bank=db.query(Bank).first()
    if not bank:
        raise HTTPException(
            detail='bank does not exist',
            status_code=401
        )
    role_exist=db.query(Role).filter(Role.name=='customer').first()
    if not role_exist:
        raise HTTPException(
            detail='role does not exist',
            status_code=401
        )
    password=get_password_hash(customer.password)
    user=User(username=customer.username,
              phone_number=customer.phone_number,
              email=customer.email
              ,password=password,role_id=role_exist.id,bank_id=bank.id)
    db.add(user)
    db.commit()
    db.refresh(user)

    email=EmailLog(
        title='user registration successfull',
        body=f"the user hase been created successfyll the the username as {user.username} and password as {user.password}"
        ,recipient=user.email,

    )
    db.add(email)
    db.commit()
    db.refresh(email)
    background_task.add_task(
        send_email,
        to_email=email.recipient,
        subject=email.title,
        title=email.body
        )
    
    manage=Manage(
        subordinate_id=user.id,
        manager_id=ma.id
    )
    db.add(manage)
    db.commit()

    wallet=Wallet()
    wallet.user_id=user.id 
    wallet.is_bank=False
    db.add(wallet)

    db.commit()
    db.refresh(wallet)
    return user

@users_router.post('/relationship/manager',response_model=UserBase)
async def create_relationship_manager(
    user:RmCreate,
    db:Session=Depends(connect),
    us:User=Depends(RoleChecker(['admin']))
):
    bank_exist=db.query(Bank).first()
    if not bank_exist:
        raise HTTPException(
            detail='bank not created',
            status_code=400
        )
    
    role_exist=db.query(Role).filter(Role.name=='relation manager').first()
    if not role_exist:
        raise HTTPException(
            detail='role is not created yet',
            status_code=402
        )
    user_exist=db.query(User).filter(User.username==user.username).first()
    if user_exist:
        raise HTTPException(
            detail='user with username already exist',
            status_code=401)
    
    password=get_password_hash(user.password)
    user=User(username=user.username,
            password=password,
            phone_number=user.phone_number,
            email=user.email,
            bank_id=bank_exist.id,
            role_id=role_exist.id)
    db.add(user)
    db.commit()
    db.refresh(user)
    manage=Manage(
        subordinate_id=user.id,
        manager_id=us.id
    )
    db.add(manage)
    db.commit()
    wallet=Wallet()
    wallet.user_id=user.id
    wallet.is_bank=False
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return user

@users_router.delete('/{id}')
async def delete_user(id:int,
    db:Session=Depends(connect),                  
    cuser:User=Depends(RoleChecker(['admin']))):
    users=db.query(User).filter(User.id==id).first()
    if not users:
        raise HTTPException(
            detail='user not found',
            status_code=status.HTTP_404_NOT_FOUND
        )
    db.delete(users)
    db.commit()
    

@users_router.get('/all',response_model=List[UserBase])
async def get_all_users(
    user:User=Depends(RoleChecker(['admin'])),
    db:Session=Depends(connect)):
    return db.query(User).all()


@users_router.get("/users/me/", response_model=UserBase)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user

@users_router.post('/refer/new/user')
async def refer_new_user(
    payload:ReferUserName,
    user:User=Depends(RoleChecker(['customer'])),
    db:Session=Depends(connect)):
    refered_user=db.query(User).filter(User.username==payload.username).first()
    if not refered_user:
        raise HTTPException(
            detail='user does not exist',
            status_code=405
        )
    
    #preventing self referal
   # if refered_user.id==user.id:
    #    raise HTTPException(
     #       status_code=400,
      #      detail='you cannot refer yourself'
       # )
    
    # check already referred (ONE-TO-ONE rule)
    if refered_user.referal_recieved:
        raise HTTPException(
            status_code=400,
            detail="User already referred"
        )
    
     # create referral
    referral = Referal(
        referrer_id=user.id,
        referred_id=refered_user.id,
        amount=0.0,
        status='eligible'
    )

    db.add(referral)
    db.commit()

    return {"message": "Referral created successfully"}
    

@users_router.get('/my/referals',response_model=List[ReferedUser])
async def get_users_refered_by_me(
    db:Session=Depends(connect),
    user:User=Depends(RoleChecker(['customer']))
):
    
    referals=user.referals_made
    return [user.referred for user in referals]

@users_router.get('/user/surbodinates',response_model=list[UserBase])
async def get_user_managed_by(
    db:Session=Depends(connect),
    user:User=Depends(RoleChecker(['relation_manager','admin']))
):
    return [m.subordinate for m in user.managing]


@users_router.get('/user/manager',response_model=UserBase)
async def get_my_manager(
    db:Session=Depends(connect),
    user:User=Depends(get_current_active_user)
):
    return user.managed_by.manager

'''

@users_router.post('/token')
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm=Depends(),
    db:Session=Depends(connect)
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username,"role":user.role.name}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
'''