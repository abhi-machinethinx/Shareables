import requests
import os

def upload():
    url = 'http://172.172.172.122:6005/rcv_code'
    files = {'file': ('uploaded.zip', open('imagezmq-master.zip', 'rb'))}

    r = requests.post(url, files=files)
    if r.status_code == 200:
        print("Uploaded Successfully")

upload()
