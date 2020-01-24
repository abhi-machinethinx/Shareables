import requests
import os
import time
from datetime import datetime

def upload():
    url = 'http://192.168.4.2:6005/rcv_code'
    # files = {'file': ('process_test.py', open('C:/Users/Admin/Documents/Python_Scripts/Performance_Tests/process_test.py', 'rb'))}
    # files = {'file': ('analyse_video.py', open('C:/Users/Admin/Documents/Python_Scripts/Cerberus_V1/analyse_video.py', 'rb'))}
    files = {'file': ('group1.jpg', open('Cerberus_V1.zip', 'rb'))}

    r = requests.post(url, files=files)
    if r.status_code == 200:
        print("Uploaded Successfully")

def uploadFiles():
    dir = "Send/"
    url = 'http://192.168.4.138:6005/rcv_code'
        
    for f in os.listdir(dir):
        files = {'file': (f, open(dir+f, 'rb'))}

        r = requests.post(url, files=files)
        if r.status_code == 200:
            print("Uploaded Successfully")


def uploadVideo():
    url = "http://192.168.4.2:6123/rcv_video"
    try:
        loop = 4
        for i in range(loop):
            filename = "C:/Users/Admin/Documents/Python_Scripts/Performance_Tests/test.mp4"
            videoFile = open(filename, 'rb')
            newname = str(datetime.now().time())
            newname = newname[:newname.find(".")]
            newname = newname.replace(":","")
            files = {'file': (newname+".mp4", videoFile)}
            data = {"cam_auth_id": "CAM-AUTH-100", "date": "2020-01-20", "activityId": "ACT11"+str(i)}
            res = requests.post(url=url, data=data, files=files)
            videoFile.close()

            if res.status_code == 200:
                print("Video ",filename," uploaded successfully.")
                
        
    except Exception as ex:
        print("ERROR: In save_video.send_video():", ex)

def apiTest():
    url="http://182.156.211.186:8484/cerberus"
    data = {}
    res = requests.post(url=url, data=data)
    if res.status_code == 200:
        print("API hit success.")
            

# upload()
uploadFiles()
# uploadVideo()
# apiTest()
