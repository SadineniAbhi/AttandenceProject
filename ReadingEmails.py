# This application reads Emails and runs two times every day expect sunday and second-saturday
import datetime
import email
import imaplib
import sqlite3

#this block creates the database
con = sqlite3.Connection("attendence.db")
cursor = con.cursor()

#This creates the table attendence
cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendence(
        date DATE PRIMARY KEY,
        time TIME,
        M TEXT,
        E TEXT
    )
    ''')

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
timestring = None

#This block is used to get date, time , status of the biometrics.
if 'style="color:#DF0101">failed' not in data:
    status = data[108]
    date = data[117]
    time = data[119]
    status = status[3:13]
    date = date[3:13]
    time = time[3:]

#this block get the date as stirng in us format
date_parts = date.split('/')
date = f'{date_parts[2]}-{date_parts[1]}-{date_parts[0]}'

#this block creates time object
if time!= None:
    time = datetime.datetime.strptime(time, "%H:%M:%S").time()


#db sesctions starts here
if status and date == str(datetime.date.today()):
    dbdate = None
    dbtimestring = None
    for i in cursor.execute('''SELECT date,time FROM attendence WHERE date = ? ''',(date,)):
        dbdate,dbtimestring = i
    #this block converts the dbtimestring into timeobject
    if dbtimestring!=None:
        dbtime = datetime.datetime.strptime(dbtimestring, "%H:%M:%S").time()
    if date != dbdate:
        cursor.execute('''INSERT INTO attendence VALUES(?,?,'p','a')''', (date, str(time)))
    elif date == dbdate:
        six_hours = datetime.timedelta(hours=6)
        time_difference = datetime.timedelta(hours=time.hour - dbtime.hour, minutes=time.minute - dbtime.minute,
                                             seconds=time.second - dbtime.second)
        if time_difference>six_hours:
            value = 'p'
            cursor.execute('''
                UPDATE attendence
                SET E = ?
                WHERE date = ?
            ''', (value, date))
con.commit()

for i in cursor.execute('''SELECT * FROM attendence'''):
    print(i)