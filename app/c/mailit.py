import smtplib
import sys
import os

SERVER = "localhost"

FROM = os.getlogin()
TO = [raw_input("To : ")]

SUBJECT = "Message From " + os.getlogin()

print "Message : (End with ^D)"
TEXT = ''
while 1:
    line = sys.stdin.readline()
    if not line:
        break
    TEXT = TEXT + line

# Prepare actual message

message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(TO), SUBJECT, TEXT)

# Send the mail

server = smtplib.SMTP(SERVER, 1025)
server.sendmail(FROM, TO, message)
server.quit()