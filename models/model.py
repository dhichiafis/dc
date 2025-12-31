from sqlalchemy import Column,Boolean,Float,Integer,ForeignKey,String,DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from database import *

class Bank(Base):
    __tablename__='banks'
    id=Column('id',Integer,primary_key=True)
    name=Column('name',String,unique=True)

    users=relationship('User',back_populates='bank')
    wallet=relationship('Wallet',back_populates='bank')
    
class Role(Base):
    __tablename__='roles'
    id=Column('id',Integer,primary_key=True)
    name=Column('name',String,unique=True)
    users=relationship('User',back_populates='role')

class User(Base):
    __tablename__='users'
    id=Column('id',Integer,primary_key=True)
    role_id=Column('role_id',Integer,ForeignKey('roles.id'))
    bank_id=Column('bank_id',Integer,ForeignKey('banks.id'))

    username=Column('username',String,unique=True)
    password=Column('password',String)
    phone_number=Column('phone_number',String,unique=True)
    created_at=Column('created_at',DateTime,default=datetime.now)
    updated_at=Column('updated_at',DateTime,default=datetime.now)
    bank=relationship('Bank',back_populates='users')
    role=relationship('Role',back_populates='users')

    wallet=relationship('Wallet',back_populates='user')
    products=relationship('Product',back_populates='creator')
    bonuses=relationship('Bonus',back_populates='customer')

    purchases_as_customer = relationship(
        "Purchase",
        foreign_keys="Purchase.customer_id",
        back_populates="customer"
    )

    purchases_as_seller = relationship(
        "Purchase",
        foreign_keys="Purchase.seller_id",
        back_populates="seller"
    )


class Product(Base):
    __tablename__='products'
    id=Column('id',Integer,primary_key=True)
    user_id=Column('user_id',Integer,ForeignKey('users.id'))
    title=Column('title',String,unique=True)
    description=Column('description',String)
    created_at=Column('created_at',DateTime,default=datetime.now)

    creator=relationship('User',back_populates='products')
    purchases=relationship('Purchase',back_populates='product')

class Bonus(Base):
    __tablename__='bonus'
    id=Column('id',Integer,primary_key=True)
    purchase_id=Column('purchase_id',Integer,ForeignKey('purchases.id'))
    user_id=Column('user_id',Integer,ForeignKey('users.id'))
    amount=Column('amount',Float)
    title=Column('title',String)
    image=Column('image',String)#mpesa image
    status=Column('status',String)#claim,create,approved rejected 
    paid_at=Column('paid_at',DateTime,default=datetime.now)
    created_at=Column('created_at',DateTime,default=datetime.now)
    updated_at=Column('updated_at',DateTime,default=datetime.now)

    purchase = relationship("Purchase", back_populates="bonus")
    customer = relationship("User", back_populates="bonuses")

    #users=relationship('User',back_populates='bonus')
    #product=relationship('Product',back_populates='bonus')


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True)

    product_id = Column(Integer, ForeignKey("products.id"))
    customer_id = Column(Integer, ForeignKey("users.id"))
    seller_id = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime, default=datetime.now)

    product = relationship("Product",back_populates='purchases')
    customer = relationship("User", foreign_keys=[customer_id],back_populates="purchases_as_customer")
    seller = relationship("User", foreign_keys=[seller_id],back_populates='purchases_as_seller')

    bonus = relationship("Bonus", uselist=False, back_populates="purchase")




class Wallet(Base):
    __tablename__='wallets'
    id=Column('id',Integer,primary_key=True)
    user_id=Column('user_id',Integer,ForeignKey('users.id'),nullable=True)
    bank_id=Column('bank_id',Integer,ForeignKey('banks.id'),nullable=True)
    is_bank=Column('is_bank',Boolean,default=False)
    created_at=Column('created_at',DateTime,default=datetime.now)

    user=relationship('User',back_populates='wallet')
    bank=relationship('Bank',back_populates='wallet')
    accounts=relationship('Account',back_populates='wallet')
    transactions=relationship('Transaction',back_populates='wallet')


class Account(Base):
    __tablename__='accounts'
    id=Column('id',Integer,primary_key=True)
    wallet_id=Column('wallet_id',Integer,ForeignKey('wallets.id'))
    name=Column('name',String,unique=True)
    type=Column('type',String)
    balance=Column('balance',Float)
    created_at=Column('created_at',DateTime,default=datetime.now)
    updated_at=Column('updated_at',DateTime,default=datetime.now)

    entries=relationship('Entry',back_populates='account')
    wallet=relationship('Wallet',back_populates='accounts')

class Transaction(Base):
    __tablename__='transactions'
    id=Column('id',Integer,primary_key=True)
    type=Column('type',String)
    wallet_id=Column('wallet_id',Integer,ForeignKey('wallets.id'))
    amount=Column('amount',Float,default=0.0)
    description=Column('description',String)
    mpesa_receipt=Column('mpesa_reciept',String,nullable=True)#these two fields are useful for audit
    checkout_id=Column('checkout_id',String,nullable=True)#now the transaction is asynchronous the user has not enter pin so we have to wait 
   
    status=Column('status',String)#a transaction can be pending completed,failed
    created_at=Column('created_at',DateTime,default=datetime.now)
   # checkout_request_id = Column(String, unique=True, nullable=True)
    entries=relationship('Entry',back_populates='transaction')
    wallet=relationship('Wallet',back_populates='transactions')

class Entry(Base):
    __tablename__='entries'
    id=Column('id',Integer,primary_key=True)
    account_id=Column('account_id',Integer,ForeignKey('accounts.id'))
    transaction_id=Column('transaction_id',Integer,ForeignKey('transactions.id'))
    description=Column('description',String)
    credit=Column('credit',Float)
    debit=Column('debit',Float)
    created_at=Column('created_at',DateTime,default=datetime.now)

    transaction=relationship('Transaction',back_populates='entries')
    account=relationship('Account',back_populates='entries')

