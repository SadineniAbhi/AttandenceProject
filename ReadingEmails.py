# This application reads Emails and runs two times every day expect sunday and second-saturday
import datetime
import logging
import email
import imaplib
import sqlite3

#google mysql connector
import mysql.connector
from mysql.connector.constants import ClientFlag

logging.basicConfig(filename='logs.log',level=logging.DEBUG)

config = {
    'user': 'Enter your user',
    'password': 'Enter your password',
    'host': 'Enter your host name/ip',
    'client_flags': [ClientFlag.SSL],
    #set the ssl crtificaties paths
    'ssl_ca': r'/enter/path',
    'ssl_cert': r'/enter/path',
    'ssl_key': r'/enter/path',
}
#this block creates cursor
config['database'] = 'Enter your database name'
cnxn = mysql.connector.connect(**config)
cursor = cnxn.cursor()


#This creates the table attendence
cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance(
        date DATE PRIMARY KEY,
        time TIME,
        M TEXT,
        E TEXT
    )
    ''')
cnxn.commit()
cursor.close()


#this block connects to my email
M = imaplib.IMAP4_SSL("imap.gmail.com")
M.login('Enter your email', 'enter your password')
M.select('inbox')

#this block gets the body of email in html code.
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

#This block is used to get date, time , status of the biometrics.
if 'style="color:#DF0101">failed' not in data:
    status = data[108]
    date = data[117]
    time = data[119]
    status = status[3:13]
    date = date[3:13]
    time = time[3:]


#this block gets the date and time objects
if status == 'successful':
    date_parts = date.split('/')
    date = f'{date_parts[2]}-{date_parts[1]}-{date_parts[0]}'
    date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

    #this block create a timedelta object
    time_parts = time.split(':')
    hours = int(time_parts[0])
    minutes = int(time_parts[1])
    seconds = int(time_parts[2])
    time= datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

# db --- database inintalized to None if the enrty is not present in db
dbdate = None
dbtime = None
cursor = cnxn.cursor()
# This block get the dbtime,dbdate
cursor.execute('''SELECT date, time FROM attendance WHERE date = %s''', (date,))
result = cursor.fetchone()
if result is not None:
    dbdate, dbtime = result
cursor.close()

#db sesctions starts here
if datetime.date.today().weekday() != 6:
    if status == 'successful' and date == datetime.date.today():
        cursor = cnxn.cursor()
        #This block doesn't gets executed if date == dbdate
        #this block marks morning attendance
        if date != dbdate:
            cursor.execute('''INSERT INTO attendance VALUES(%s,%s,'p','a')''', (date, time))
            logging.debug("Marking present morning half on {}".format(date))
            cnxn.commit()
            cursor.close()

        #if date is already present in database then it marks evening attendance
        elif date == dbdate:

            #creates sixhours time gap vaiable and caluates the diffrence between the time
            six_hours = datetime.timedelta(hours=6)
            time_difference = time - dbtime
            #this block check time diffrence and marks the attendance
            cursor = cnxn.cursor()
            if time_difference>six_hours:
                value = 'p'
                cursor.execute('''
                    UPDATE attendance
                    SET E = %s
                    WHERE date = %s
                ''', (value, date))
                logging.debug("Marking present evening half on {} and time difference is {}".format(date,time_difference))
                cnxn.commit()
                cursor.close()
    else:
        #if statement to avoid primary key error.
        if date != dbdate:
            logging.debug("you didn't mark attendance at morning marking absent")
            cursor = cnxn.cursor()
            cursor.execute('''INSERT INTO attendance VALUES(%s,%s,'a','a')''', (datetime.date.today(), datetime.timedelta(hours = 4)))
            cnxn.commit()
            cursor.close()
else:
    logging.debug("today {} is sunday".format(datetime.date.today()))
