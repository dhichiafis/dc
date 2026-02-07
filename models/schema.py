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
    DISBURSED='disbursed'
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
    email:str 
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

class FeatureCreate(BaseModel):
    name:str 
class FeatureRead(FeatureCreate):
    id:int 
    product_id:int 
    model_config=ConfigDict(from_attributes=True)

class ProductCreate(BaseModel):
    title: str
    description: str
    image:str 


class ProductRead(ProductCreate):
    id: int
    user_id:int
    created_at: datetime
    feateures:List[FeatureRead]=[]

    model_config = ConfigDict(from_attributes=True)

class PurchaseCreate(BaseModel):
    product_id: int
    
    
class PurchaseRead(BaseModel):
    id: int
    product_id: int|None=None
    customer_id: int
    seller_id: int
    created_at: datetime
    product:ProductRead|None=None
    model_config = ConfigDict(from_attributes=True)


class h(BaseModel):
    id: int
    created_at: datetime
    product: ProductRead
    customer: UserCreate
    seller: UserCreate

    model_config = ConfigDict(from_attributes=True)

class CustomerCreate(BaseModel):
    username:str 
    password:str 
    email:str|None=None 
    phone_number:str 

class BankAdmin(BaseModel):
    bank_name:str 
    username:str 
    phone_number:str 
    email:str|None=None
    password:str 


class RmCreate(BaseModel):
    username:str 
    password:str 
    phone_number:str 
    email:str|None=None


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
    type:Optional[str]=None 
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

    purchase: PurchaseRead | None=None
    customer: UserBase | None = None

    model_config = ConfigDict(from_attributes=True)


class ReferedUser(BaseModel):
    id:int 
    username: str
    phone_number: str
    created_at:datetime


class ProfileCreate(BaseModel):
    status:str 
    funded_amount:float
    funded_status:str

class ProfileBase(ProfileCreate):
    id:int 

    created_at:datetime
    updated_at:datetime
    model_config=ConfigDict(from_attributes=True)

class EmailLogCreate(BaseModel):
    id:int 
    titl:str
    body:str 
    recipient:str 
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)