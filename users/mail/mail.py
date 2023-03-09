import smtplib
from email.message import EmailMessage
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove

def replace(file_path, token):
    #Create temp file
    with open(file_path) as base_file:
        data = base_file.readlines()
    line = data[0]
    info = token + "\n"
    data[0] = line.rstrip("\n") + info

    with open("message.txt", "r+") as new_file:
        for line in data:
            new_file.write(line)
    return base_file

def send_mail(recipient, token):

    replace("base.txt", token)
    with open("message.txt", "r") as fp:
        pass


if __name__ == "__main__":
    send_mail("dincoionut49@gmail.com", "4r3fefefr3r3r")