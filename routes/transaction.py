from fastapi import APIRouter,Depends,HTTPException,status,Request
from sqlalchemy.orm import Session 
from database import *
from models.model import *
from models.schema import *
from security import *
from payment import *
from fastapi import BackgroundTasks

transaction_router=APIRouter(prefix='/transactions',tags=['transactions'])



@transaction_router.post('/relation/manager/deposit'
    ,response_model=TransactionBase)
async def relation_manager_deposit(
    trans:TransactionCreate,
    background_tasks: BackgroundTasks,
    user:User=Depends(RoleChecker(['relation manager'])),
    db:Session=Depends(connect)):
    
    wallet=db.query(Wallet).filter(Wallet.user_id==user.id).first()
    if not wallet:
        raise HTTPException(
            detail='wallet for the user does not',
            status_code=403
        )
    #stk push to deposit since we are depositing into our account i expect it htoe be the following 
    print(user.phone_number)
    formatted_phone_number = format_phone_number(user.phone_number)
    response = send_prompt_push(formatted_phone_number, trans.amount)
    #response=send_prompt_push(user.phone_number,trans.amount)
    
    transaction=Transaction(description=trans.description,
           amount=trans.amount,
           wallet_id=wallet.id,
                         
        )
    transaction.checkout_id=response.get('CheckoutRequestID')
    transaction.status='pending'
    transaction.type="deposit"
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    print(response)
    #its herer that when the transaction is successfull we record the debit and credit right
    #if the transaction is not successfull then the transaction status is turned to fiaild 
    
    
    return transaction


#our real stk push happens in the callback which we are going to expose to ngrok
#as a testing ground

@transaction_router.post("/mpesa/callback")
async def mpesa_callback(request: Request, db: Session = Depends(connect)):
    payload = await request.json()

    stk = payload["Body"]["stkCallback"]
    checkout_id = stk["CheckoutRequestID"]
    result_code = stk["ResultCode"]

    transaction = db.query(Transaction).filter(
        Transaction.checkout_id == checkout_id
    ).first()

    # Always acknowledge Safaricom
    if not transaction:
        return {"ResultCode": 0, "ResultDesc": "Accepted"}

    if result_code == 0:
        # ✅ PAYMENT SUCCESS
        transaction.status = "completed"

        # Extract MpesaReceiptNumber
        receipt = None
        for item in stk.get("CallbackMetadata", {}).get("Item", []):
            if item.get("Name") == "MpesaReceiptNumber":
                receipt = item.get("Value")
                break

        transaction.mpesa_receipt = receipt

        # Create accounting entries
        cash_account = db.query(Account).filter(Account.name == "Cash Account").first()
        deposit_account = db.query(Account).filter(Account.name == "Bank Deposit").first()

        if not cash_account or not deposit_account:
            raise HTTPException(status_code=400, detail="Account does not exist")

        cash_entry = Entry(
            description=transaction.description,
            debit=transaction.amount,
            credit=0.0,
            account_id=cash_account.id,
            transaction_id=transaction.id
        )

        deposit_entry = Entry(
            description=transaction.description,
            debit=0.0,
            credit=transaction.amount,
            account_id=deposit_account.id,
            transaction_id=transaction.id
        )

        db.add_all([cash_entry, deposit_entry])

    else:
        # ❌ PAYMENT FAILED / CANCELLED
        transaction.status = "failed"

    db.commit()

    return {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }


@transaction_router.post('/payment/callback')
async def process_payment_callback(
    request:Request,db:Session=Depends(connect)):
    payload=await request.json()
    payment_callback=payload.get("Result")

    print(payment_callback)
    if not payment_callback:
        return {}
    conversation_id=payment_callback.get("ConversationID")
    transaction_id=payment_callback.get('TransactionID')
    result_code=payment_callback.get('ResultCode')
    #find the transaction wit the checkout id
    transaction=db.query(Transaction).filter(
        Transaction.checkout_id==conversation_id).first()
    if not transaction:
        return {"ResultCode": 0, 
                "ResultDesc": "Transaction not found"}
    if result_code==0:
        transaction.status="successful"
        transaction.mpesa_receipt=transaction_id

        cash_account = db.query(Account).filter(Account.name == "Cash Account").first()
        deposit_account = db.query(Account).filter(Account.name == "Bank Deposit").first()

        if not cash_account or not deposit_account:
            raise HTTPException(status_code=400, detail="Account does not exist")

        cash_entry = Entry(
            description=transaction.description,
            debit=transaction.amount,
            credit=0.0,
            account_id=cash_account.id,
            transaction_id=transaction.id
        )

        deposit_entry = Entry(
            description=transaction.description,
            debit=0.0,
            credit=transaction.amount,
            account_id=deposit_account.id,
            transaction_id=transaction.id
        )

        db.add_all([cash_entry, deposit_entry])
    else:
        transaction.status="failed"
    db.commit()



'''
@transaction_router.post("/mpesa/callback")
async def mpesa_callback(request: Request, db: Session = Depends(connect)):
    payload = await request.json()

    stk = payload["Body"]["stkCallback"]
    checkout_id = stk["CheckoutRequestID"]
    result_code = stk["ResultCode"]

    transaction = db.query(Transaction).filter(
        Transaction.checkout_id == checkout_id
    ).first()

    if not transaction:
        return {"ResultCode": 1, "ResultDesc": "Transaction not found"}

    # Handle successful payment
    if result_code == 0:
        callback_metadata = stk.get("CallbackMetadata", {}).get("Item", [])
        receipt = None
        for item in callback_metadata:
            if item.get("Name") == "MpesaReceiptNumber":
                receipt = item.get("Value")
                break
        transaction.status = "success"
        transaction.mpesa_receipt = receipt
    else:
        # Payment failed or cancelled
        transaction.status = "failed"
        cash_account=db.query(Account).filter(Account.name=='Cash Account').first()
        deposit_account=db.query(Account).filter(Account.name=='Bank Deposit').first()

        if not cash_account:
            raise HTTPException(
                detail='account does not exist',
            status_code=400
            )
        if not deposit_account:
            raise HTTPException(
            detail='account does not exist',
            status_code=400
            )
        cash_entry=Entry(description=transaction.description,
            debit=transaction.amount,
            credit=0.0,
            account_id=cash_account.id,
            transaction_id=transaction.id
            )
    
        deposit_entry=Entry(description=transaction.description,
                    debit=0.0,credit=transaction.amount,
                    account_id=deposit_account.id,
                    transaction_id=transaction.id
                    )
        db.add_all([cash_entry,deposit_entry])
        db.commit()
        db.refresh(cash_entry)
        db.refresh(deposit_entry)
    
        
    
    
    else:
        transaction.status = "failed"

    db.commit()

    # Safaricom expects THIS
    return {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }

'''

@transaction_router.get('/by/me',response_model=list[TransactionBase])
async def get_transactions_by_rm(
    db:Session=Depends(connect),
    user:User=Depends(RoleChecker(['relation manager','admin']))
):
    transactions = (
    db.query(Transaction)
    .join(Transaction.wallet)  # join the Wallet table
    .filter(Wallet.user_id == user.id)
    .all()
)   
    return transactions

@transaction_router.get('/all',response_model=list[TransactionBase])
async def get_all_transactions(
    db:Session=Depends(connect),
    user:User=Depends(RoleChecker(['admin']))
):
    transactions=db.query(Transaction).all()
    return transactions



'''
@transaction_router.post('/relation/manager/deposit', response_model=TransactionBase)
async def relation_manager_deposit(
    trans: TransactionCreate,
    user: User = Depends(RoleChecker(['relation manager'])),
    db: Session = Depends(connect)
):
    print(user.role.name)
    print(user)
    # Fetch wallet
    wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()

    # Correct logic
    if not wallet:
        raise HTTPException(
            detail='Wallet for this user does not exist',
            status_code=403
        )

    # Create transaction
    transaction = Transaction(
        description=trans.description,
        amount=trans.amount,
        wallet_id=wallet.id                 
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # Fetch accounts
    cash_account = db.query(Account).filter(Account.name == 'Cash Account').first()
    deposit_account = db.query(Account).filter(Account.name == 'Bank Deposit').first()

    if not cash_account or not deposit_account:
        raise HTTPException(
            detail='Required accounts do not exist',
            status_code=400
        )

    # Create entries
    cash_entry = Entry(
        description=trans.description,
        debit=transaction.amount,
        credit=0.0,
        account_id=cash_account.id,
        transaction_id=transaction.id
    )
    
    deposit_entry = Entry(
        description=trans.description,
        debit=0.0,
        credit=transaction.amount,
        account_id=deposit_account.id,
        transaction_id=transaction.id
    )

    db.add_all([cash_entry, deposit_entry])
    db.commit()

    return transaction
'''