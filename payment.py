import requests 
import json 
from requests.auth import HTTPBasicAuth
from datetime import timedelta,time,datetime
import base64

def get_access_token():
    #url="https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    #CONSUMER_KEY="kYrR8xjbpOa5XjRLuChNmcYaK8SEXzj2tyqaAV1mRc1ZtQvw"
    #CONSUMER_SECRET="XgXv9N8IF6pCjSCmtKFegYPDfxIcHWo8lZdRJNuf0jUExSAJsbOKtoSvAC9G9JhI"
    #replaced with live mpesa details 
    url="https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    CONSUMER_KEY="dvK5OJjyrB72m5OQTLPIlva150Pn7zw0hZNCFZXhpA5tKZLF"
    CONSUMER_SECRET="r8yjL9yLCjVU6ftDGHzRHrDfPW5jlKYVfPCyANoaCAyazx38oczdi9xh3GtYWgVd"
    basic=HTTPBasicAuth(CONSUMER_KEY,CONSUMER_SECRET)
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


def send_prompt_push(phone_number,amount):
    print('stk call is initiated')
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
  "CallBackURL": "https://www.msale.xyz/transactions/mpesa/callback"
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



def disburse_payments(phone_number,amount):
    #url="https://sandbox.safaricom.co.ke/mpesa/b2c/v3/paymentrequest"
    #replace with live url
    url="https://api.safaricom.co.ke/mpesa/b2c/v1/paymentrequest"
    #replace with live shortcode
    shortcode="4002159"
    body={
        "OriginatorConversationID": "a6351cf491ef493c831d82e337d4e2b4", 
    "InitiatorName": "odhisochitigaone", 
    "SecurityCredential": "gZGr4HXHlgiNvGGJoJKKdfGb7bGbh0oCWvK1ipfjOp9+jQ/S0Mn8OT2LURuHlJHVmeHsGhgiFyW0nvplbLDyYG9ipLrctsnLIuc2DNm9+9ftZk5fgVjKNRm2Jmn1NU6nK1bi1j06VV5rkOVs30qnuO1cJnTqGyf2ahf1Q6soaIakHgDbflYi92PVAnCgzcFgUAiV7xIT9VO0nAonoBzyVkmUc0rORScWRHiBmL6C1Smeyjn/FpBq3bejx/d26jNi11MpJKmmXvxjJ0WzT3veFkmrlvlxTZOKLPfxX9rdR0Zs+CMwOyLgCPAXk74XIGqFhoW2vRkaJuZxT7SUIYgOkw==", 
    "CommandID": "BusinessPayment", 
    "Amount": int(amount), 
    "PartyA": shortcode, 
    "PartyB": phone_number, 
    "Remarks": "remarked", 
    "QueueTimeOutURL": "https://mydomain.com/path", 
    "ResultURL": "https://www.msale.xyz/transactions/payment/callback", 
    "Occassion": "ChristmasPay" 
    }
    token=get_access_token()
    headers={
        "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
    }

    response=requests.post(
        url=url,
        json=body,
        headers=headers
    )
    if response.status_code==200:
        print(response.json())
    else:
        print('faild to post')
    data= response.json()
    if data.get("ResponseCode") != "0":
        raise Exception(f"B2C Failed: {data}")

    return data


def format_phone_number(phone_number: str) -> str:
    # Ensure the phone number starts with '254' and remove any extra characters like spaces or '+'
    if phone_number.startswith('0'):
        phone_number = '254' + phone_number[1:]
    elif phone_number.startswith('+'):
        phone_number = '254' + phone_number[1:]
    return phone_number

#result=disburse_payments(phone_number="254721676091",amount=10)
#print(result)