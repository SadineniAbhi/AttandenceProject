# This application reads Emails and runs two times every day expect sunday and second-saturday
from datetime import datetime
import email
import imaplib

#this block connects to my email
M = imaplib.IMAP4_SSL("imap.gmail.com")
M.login('abhisadineni@gmail.com', 'xdho kfaa yfyk krpp')
M.select('inbox')

#this block generates the body of email in html code.
typ, data = M.search(None,"FROM aadhaar@uidai.gov.in")
email_id = data[0]
splited_email = email_id.split(b' ')
email_id = splited_email[-1]
result,email_data = M.fetch(email_id,'(RFC822)')
raw_email = email_data[0][1]
raw_email_string = raw_email.decode('utf-8')
email_message = email.message_from_string(raw_email_string)
body = None
for part in email_message.walk():
    if part.get_content_type() == 'text/html':
        body = part.get_payload(decode=True)
body = body.decode()

#this line splits the html code into a list
data  = body.split(' ')

#This Variable is used futher below to check whether biometric is sucssefull or not for inputing into database
status = None
ptime = None

#This block is used to get date, time , status of the biometrics.
if 'style="color:#DF0101">failed' not in data:
    status = data[108]
    date = data[117]
    time = data[119]
    status = status[3:13]
    date = date[3:13]
    date= datetime.strptime(date, "%d/%m/%Y").date()
    time = time[3:]
    time = datetime.strptime(time, "%H:%M:%S").time()