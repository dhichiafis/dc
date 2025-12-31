from pydantic import BaseModel,ConfigDict
from typing import List ,Optional
from enum import Enum 
from datetime import datetime

class AccountType(str,Enum):
    ASSET='asset'
    LIABILITY='liability'
    INCOME='income'
    EXPENSE='expense'
    EQUITY='equity'

class BonusStatus(str,Enum):
    CREATED='created'
    CLAIM='claim'
    APPROVED='approved'
    REJECTED='rejected'


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    #role:str 
    # intrdoduct because of rback wheree our token stores the role 

class RoleCreate(BaseModel):
    name:str 

class RoleBase(RoleCreate):
    id:int 
    model_config=ConfigDict(form_attributes=True)

class UserCreate(BaseModel):
    username:str 
    password:str 


class UserBase(BaseModel):
    id:int 
    username:str
    phone_number:str 
    role_id:int 
    bank_id:int 
    role:RoleBase
    
    model_config=ConfigDict(form_attributes=True)

class BankCreate(BaseModel):
    name:str 

class BankBase(BankCreate):
    id:int 
    users:List[UserBase]
    model_config=ConfigDict(form_attributes=True)

class ProductCreate(BaseModel):
    title: str
    description: str


class ProductRead(ProductCreate):
    id: int
    user_id:int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PurchaseCreate(BaseModel):
    product_id: int
    customer_id: int
    seller_id: int


class PurchaseRead(BaseModel):
    id: int
    created_at: datetime
    product: ProductRead
    customer: UserCreate
    seller: UserCreate

    model_config = ConfigDict(from_attributes=True)

class CustomerCreate(BaseModel):
    username:str 
    password:str 
    phone_number:str 

class BankAdmin(BaseModel):
    bank_name:str 
    username:str 
    phone_number:str 
    password:str 


class RmCreate(BaseModel):
    username:str 
    password:str 
    phone_number:str 


class EntryCreate(BaseModel):
    description:str 
    credit:float 
    debit:float 

class EntryBase(EntryCreate):
    id:int 
    account_id:int 
    transaction_id:int 
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)

class TransactionCreate(BaseModel):
    amount:float 
    description:str
   


class TransactionBase(TransactionCreate):
    id:int
    status:str
    type:str 
    created_at:datetime 
    mpesa_receipt:Optional[str]=None
    checkout_id:Optional[str]=None
    entries:List[EntryBase]

    model_config=ConfigDict(from_attributes=True)

class AccountCreate(BaseModel):
    type:str
    #type:AccountType
    balance:float 

class AccountBase(AccountCreate):
    id:int 
    model_config=ConfigDict(from_attributes=True)


class WalletCreate(BaseModel):
    is_bank:bool


class WalletBase(WalletCreate):
    id:int 
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)


class BonusCreate(BaseModel):
    purchase_id: int
    amount: float
    title: str
    image: Optional[str]


class BonusRead(BaseModel):
    id: int
    amount: float
    title: str
    image: Optional[str]
    status: BonusStatus
    paid_at: Optional[datetime]
    created_at: datetime

    purchase: PurchaseRead
    customer: UserCreate

    model_config = ConfigDict(from_attributes=True)