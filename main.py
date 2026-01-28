from fastapi import FastAPI,Depends,HTTPException
from routes.user import users_router
from routes.transaction import transaction_router
from routes.roles import roles_router
from routes.products import product_router
from routes.featurers import feature_router
from routes.purchase import purchase_router
from routes.bonuses import bonus_router
from routes.accounts import accounts_router
from fastapi.middleware.cors import CORSMiddleware
from database import *
from sqlalchemy.orm import Session
from models.model import *
from contextlib import asynccontextmanager
#from starlette_exporter import PrometheusMiddleware,handle_metrics


#Base.metadata.create_all(bind=engine)

def seed_accounts(db):
    account_names=['Cash Account','Bank Deposit','Cash Reward']
    account_types=['Asset','Liability','Expense']
    for name,type in zip(account_names,account_types):
        account=db.query(Account).filter(Account.name==name).first()
        if not account:
            account=Account(
                name=name,
                balance=0.0,
                type=type
            )
            db.add(account)
    db.commit()


def seed_roles(db):
    roles=['admin','customer','relation manager']
    for role in roles:
        db_role=db.query(Role).filter(Role.name==role).first()
        if not db_role:
            role_db=Role(name=role)
            db.add(role_db)
    db.commit()

@asynccontextmanager
async def lifespan(app:FastAPI):
    db=SessionFactory()
    seed_roles(db=db)
    seed_accounts(db=db)
    yield 
    db.close()

app=FastAPI(
    lifespan=lifespan,
    title="Msale",description="This is backend app that manages the sales of products and ensures that the correpondeces get rewarded based on the interaction with the rm and the product they bought")
#app.add_middleware(
 #  allow_headers=['*'],
  ## allow_credentials=True 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # must match Vue dev URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#app.add_middleware(PrometheusMiddleware,app_name="Msale")
#app.add_route('/metrics',handle_metrics)
app.include_router(users_router)
app.include_router(transaction_router)
app.include_router(accounts_router)
app.include_router(roles_router)
app.include_router(product_router)
app.include_router(purchase_router)
app.include_router(bonus_router)
app.include_router(feature_router)


@app.get('/')
async def home():
    return {'message':'welcome to msale but and get 10 back'}


