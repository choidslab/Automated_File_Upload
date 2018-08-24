"""
Created date: 2018-01-15-Mon
Modified date: 2018-05-08-Tue
Made by DS.Choi

본 프로그램은 특정 디렉토리를 모니터링 하면서 파일 생성 이벤트가 발생할 경우, 해당 파일을 FTP 서버에 자동 업로드 하는 프로그램입니다.

"""
# -*- coding: utf-8 -*-
import os
import time
import threading
import getpass
from ftplib import FTP
from tqdm import tqdm
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# FTP server remote path & OS local path
Rpath = "/phard/snji/"
Lpath = "/Users/dooseop/Desktop/2018/"

# Variables FTP UID, PWD
username = ""
password = ""


class Watcher:
    # Set Monitoring Directory
    DIRECTORY_TO_WATCH = Lpath

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        print("###### Start Monitoring ######")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()

        self.observer.join()

class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print("Received created event - %s." % event.src_path)

            # Delay some seconds in order to safety file open
            if os.path.getsize(event.src_path) >= 1073741824:
                time.sleep(10)
            else:
                time.sleep(5)

            # Extract file extension
            ext = os.path.splitext(event.src_path)[-1]

            # If file extension is '.mp4', upload a file.
            if ext == '.mp4':
                filename = event.src_path.split('/')[-1]
                dirname = event.src_path.split('/')[-2]
                t = threading.Thread(target=ftp_upload(filename, dirname, event.src_path))
                t.start()
            else:
                pass
        else:
            return None

# Function of ftp upload
def ftp_upload(filename, dirname, eventpath):

    # Login to ftp server.
    ftp = FTP("snji.org")
    ftp.login(username, password)
    #print("Connection established.")

    # File open
    file = open(eventpath, 'rb')
    filesize = os.path.getsize(eventpath)
    # Set upload path - Server path
    ftp.cwd(Rpath + dirname + "/")

    # Perform upload and Show user for progress bar
    with tqdm(unit='blocks', unit_scale=True, leave=False, miniters=1, desc="Uploading...",
              total=filesize) as tqdm_instance:
        ftp.storbinary('STOR ' + filename, file, 20480, callback=lambda sent: tqdm_instance.update(len(sent)))
    print("\nFile transfer successful.\n")

    # Close ftp server.
    ftp.quit()
    # Close file open().
    file.close()

def check_account():
    try:
        ftp = FTP("snji.org")
        ftp.login(username, password)
        ftp.close()
        return True
    except Exception as e:
        print(e)
        ftp.close()
        print("FTP close!")
        return False

if __name__ == '__main__':

    # Check FTP Account Info
    while True:
        print("###### Enter the ftp ID and Password ######")
        username = input("ID: ")
        password = getpass.getpass(prompt="Password: ")

        if check_account():
            print("Verified!\n")
            break
        else:
            print("Please check FTP ID or Password.\n")
            continue

    w = Watcher()
    w.run()
