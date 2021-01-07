"""
Created date: 2018-01-15-Mon
Modified date: 2018-12-08-Tue
Made by DS.Lab

본 프로그램은 특정 디렉토리를 모니터링 하는 중에 새로운 파일의 생성 이벤트를 감지할 경우, 해당 파일을 FTP 서버의 원하는 경로에 자동 업로드 하는 프로그램입니다.

"""
# -*- coding: utf-8 -*-
import os
import time
import getpass
from ftplib import FTP
from tqdm import tqdm
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Server URL
FTP_URL = ""

# FTP server Remote path & OS Local path
Rpath = "/phard/snji/"
Lpath = "/Users/dooseop/Desktop/2018/"

# Variables FTP User ID, Password
username = ""
password = ""


class Watcher:

    # Set Monitoring Directory
    DIRECTORY_TO_WATCH = Lpath

    def __init__(self):
        self.observer = Observer()

    def run(self):
        # 이벤트 핸들러 생성
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
            # Extract file extension
            ext = os.path.splitext(event.src_path)[-1]

            # If file extension is .mp4, print 'Create Message'
            if ext == '.mp4':
                # Take any action here when a file is first created.
                print("Created '.mp4' file - %s." % event.src_path)

            # Delay some seconds in order to safety file open
            if os.path.getsize(event.src_path) >= 1073741824:
                time.sleep(10)
            else:
                time.sleep(5)

            # If file extension is '.mp4', upload a file.
            if ext == '.mp4':
                filename = event.src_path.split('/')[-1]
                dirname = event.src_path.split('/')[-2]
                ftp_upload(filename, dirname, event.src_path)
                # t = threading.Thread(target=ftp_upload(filename, dirname, event.src_path))
                # t.start()
            else:
                pass
        else:
            return None


def ftp_upload(filename, dirname, eventpath):

    # Login to ftp server.
    ftp = FTP(FTP_URL)
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
    print("###### Monitoring ######")

    # Close connection
    ftp.quit()
    # Close file
    file.close()


def check_account():
    try:
        ftp = FTP(FTP_URL)
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
