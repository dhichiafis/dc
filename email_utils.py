from config import *
import resend 

RESEND_API_KEY=settings.RESEND_API_KEY
FROM_EMAIL=settings.FROM_EMAIL

resend.api_key=RESEND_API_KEY
def send_email(to_email,subject,title):
    params: resend.Emails.SendParams = {
    "from": FROM_EMAIL,
    "to":to_email,
    "subject": subject,
    "title":title,
    "html": "<strong>it works!</strong>",
}
    email = resend.Emails.send(params)
    print(email)

