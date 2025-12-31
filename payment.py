import requests 
import json 
from requests.auth import HTTPBasicAuth
from datetime import timedelta,time,datetime
import base64

from config import settings

def get_access_token():
    #url="https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    #CONSUMER_KEY="kYrR8xjbpOa5XjRLuChNmcYaK8SEXzj2tyqaAV1mRc1ZtQvw"
    #CONSUMER_SECRET="XgXv9N8IF6pCjSCmtKFegYPDfxIcHWo8lZdRJNuf0jUExSAJsbOKtoSvAC9G9JhI"
    #replaced with live mpesa details 
    url="https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    basic=HTTPBasicAuth(settings.CONSUMER_KEY,settings.CONSUMER_SECRET)
    response=requests.get(
        url=url,
        auth=basic
    )
    if(response.status_code==200):
        data=response.json()
        token=data['access_token']
        return token
    else:
        return {'message':'failed to get the token'}
    


def get_stk_push(phone_number,amount):

    token=get_access_token()
    url="https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    timestamp=datetime.now()
    timestampe=timestamp.strftime('%Y%m%d%H%M%S')
    #print(timestampe)

    #passkey="bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
    passkey="b810df7928546cff0698cf6a80b44506048799fa64e96645ef7cf925f4ca35c7"
    shortcode="4002159"
    data=shortcode+passkey+timestampe
    
    password=base64.b64encode(data.encode('utf-8')).decode('utf-8')
    #print(password)
    body={
  "Password":password,
  "BusinessShortCode": shortcode,
  "Timestamp": timestampe,
  "Amount": int(amount),#the amount is an integer or the callback fails to indicate success status of 
  "PartyA": phone_number,
  "PartyB": shortcode,
  "TransactionType": "CustomerPayBillOnline",
  "PhoneNumber": phone_number,
  "TransactionDesc": "Test",
  "AccountReference": "Dhichiafis Tek System",
  "CallBackURL": "https://fastapi-stk-push-implementation.onrender.com/transactions/mpesa/callback"
}
    headers={
        "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
    }

    

    response=requests.post(
        url=url,
        json=body,
        headers=headers
    )
    return response.json()


