import smtplib

#credentials included in script only for demo, do not include in prod; use environments variable instead
EMAIL_ADDRESS = 'launchmobility.urbanpilot@gmail.com'
PASSWORD = 'te$t1234567'

def send_confirmation_email(email):

  with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.ehlo() #identifies mail server for app
    smtp.starttls() #encrypt connection

    smtp.ehlo() #re-identify mail server as encrypted connection

    smtp.login(EMAIL_ADDRESS, PASSWORD)

    subject = 'test email for demo'
    body = f'test email contents: /n activate email by clicking the following link:  http://localhost:5000/confirm/{email}'

    msg = f'Contents: {subject} \n\n {body}'

    #smtp.sendmail(SENDER_ADDR, RECEIVER_ADDR)
    smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg)