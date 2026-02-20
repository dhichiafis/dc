import os  
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, SessionFactory
from models.model import Base, Account, Role
from contextlib import asynccontextmanager
#from starlette_exporter import PrometheusMiddleware, handle_metrics
from routes.user import users_router
from routes.transaction import transaction_router
from routes.roles import roles_router
from routes.products import product_router
from routes.profile import profiles_router
from routes.featurers import feature_router
from routes.purchase import purchase_router
from routes.bonuses import bonus_router
from fastapi.responses import RedirectResponse
from routes.accounts import accounts_router
from loguru import logger
import sys

from fastapi.staticfiles import StaticFiles
# OpenTelemetry imports


# -----------------------------
# Database & metadata
# -----------------------------
#Base.metadata.create_all(bind=engine)
#SQLAlchemyInstrumentor().instrument(engine=engine)

# -----------------------------
# Seed functions
# -----------------------------
def seed_accounts(db):
    account_names = ['Cash Account', 'Bank Deposit', 'Cash Reward']
    account_types = ['Asset', 'Liability', 'Expense']
    for name, type in zip(account_names, account_types):
        account = db.query(Account).filter(Account.name == name).first()
        if not account:
            account = Account(name=name, balance=0.0, type=type)
            db.add(account)
    db.commit()

def seed_roles(db):
    roles = ['admin', 'customer', 'relation manager']
    for role in roles:
        db_role = db.query(Role).filter(Role.name == role).first()
        if not db_role:
            db_role = Role(name=role)
            db.add(db_role)
    db.commit()

# -----------------------------
# Lifespan
# -----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionFactory()
    Base.metadata.create_all(bind=engine)
    seed_roles(db=db)
    seed_accounts(db=db)
    yield
    db.close()

# -----------------------------
# FastAPI app
# -----------------------------
app = FastAPI(
    lifespan=lifespan,
    title="Msale",
    description="Backend app that manages sales and rewards customers for purchases"
)
app.mount("/static", StaticFiles(directory="static"), name="static")
#FastAPIInstrumentor().instrument_app(app)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#app.add_middleware(PrometheusMiddleware, app_name="Msale")
#app.add_route("/metrics", handle_metrics)

print(os.getcwd())
#logger.add("app.log", rotation="10 MB", enqueue=True, backtrace=True, diagnose=True)  # Log to file
logger.remove()
logger.add(
    sys.stdout,
    level="INFO",
    format="{time} | {level} | {extra[app]} | {message}",
    backtrace=True,
    diagnose=True,
)

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response

# Routers

app.include_router(users_router)
app.include_router(transaction_router)
app.include_router(accounts_router)
app.include_router(roles_router)
app.include_router(profiles_router)
app.include_router(product_router)
app.include_router(purchase_router)
app.include_router(bonus_router)
app.include_router(feature_router)



# Home endpoint
@app.get("/")
async def home():
    return {"message": "Welcome to Msale! Buy and get rewards."}




@app.get("/privacy")
async def privacy_policy():
    return RedirectResponse(url="/static/privacy.html")