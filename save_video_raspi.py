import picamera
import threading
from os import remove
from json import load as JLoad
from requests import post as ReqPost
from datetime import datetime
from time import perf_counter, sleep

CONFIG = {}
SCHEDULE = []
SEND_QUEUE = []
TODAY = None


# convert string date time to


def convert_to_datetime(time):
    global TODAY
    hours = time[:time.find(":")]
    mins = time[3:time.find(":", 3)]
    secs = time[6:time.find(".")]
    return datetime(TODAY.year, TODAY.month, TODAY.day, int(hours), int(mins), int(secs))

# get activity id for the video


def get_activity(vidTime):
    global SCHEDULE
    try:
        for act in SCHEDULE:
            actStartTime = convert_to_datetime(act["start"])
            actEndTime = convert_to_datetime(act["end"])
            if vidTime >= actStartTime and vidTime <= actEndTime:
                return act["activityId"]
        return None
    except Exception as ex:
        print("ERROR: In save_video.get_activity():", ex)
        return None

# send video to nuc


def send_video():
    global SEND_QUEUE, CONFIG, TODAY

    url = "http://"+CONFIG["api"]["host"]+":" + \
        CONFIG["api"]["port"]+"/"+CONFIG["api"]["route"]
    sleep_len = CONFIG["video_length"]/2
    try:
        while True:
            if len(SEND_QUEUE) > 0:
                videoFile = open(SEND_QUEUE[0]["path"], 'rb')
                files = {'file': (SEND_QUEUE[0]["filename"], videoFile)}
                activityId = get_activity(convert_to_datetime(SEND_QUEUE[0]["time"]))
                print("Video for time:",SEND_QUEUE[0]["time"]," | Activity Id:",activityId)
                if not activityId == None:
                    data = {"cam_auth_id": CONFIG["cam_auth_id"], "date": str(
                        TODAY.date()), "activityId": activityId}
                    res = ReqPost(url=url, data=data, files=files)
                    videoFile.close()
                    
                    if res.status_code == 200:
                        print("Video ",SEND_QUEUE[0]["filename"]," uploaded successfully.")
                        
                remove(SEND_QUEUE[0]["path"])
                SEND_QUEUE.pop(0)
            
            sleep(sleep_len) 
    except Exception as ex:
        print("ERROR: In save_video.send_video():", ex)

# start raspberry pi camera

def startPiCam():
    global CONFIG, SEND_QUEUE

    try:
        videoTime = CONFIG["video_length"]  # in sec
        send_thread = threading.Thread(
                        target=send_video, daemon=True)
        send_thread.start()
        
        video_capture = picamera.PiCamera(resolution=(int(CONFIG["res_width"]),int(CONFIG["res_height"])))
        
        startTime = datetime.now()
        t = str(startTime.time())
        t = t[:t.find(".")]
        filename = t.replace(":", "-")+".h264"
        path = CONFIG["data"]+filename
        
        video_capture.start_recording(path)
        video_capture.wait_recording(videoTime)

        SEND_QUEUE.append({"time":t,"path":path,"filename":filename})
        
        while True:
            startTime = datetime.now()
            t = str(startTime.time())
            t = t[:t.find(".")]
            filename = t.replace(":", "-")+".h264"
            path = CONFIG["data"]+filename
        
            video_capture.split_recording(path)
            video_capture.wait_recording(videoTime)
            
            SEND_QUEUE.append({"time":t,"path":path,"filename":filename})

        video_capture.stop_recording()

    except Exception as ex:
        print("ERROR: In save_video_raspi.startPiCam(): ", ex)
        

def main():
    global CONFIG, TODAY, SCHEDULE

    try:
        with open("cam_config.json") as input:
            CONFIG = JLoad(input)
        TODAY = datetime.now()
        # TODAY = datetime(2020,1,13,11,30,58)
        with open(CONFIG["activity"]) as act:
            data = JLoad(act)
            SCHEDULE = data[CONFIG["classId"]][str(TODAY.weekday())]

        startPiCam()
    except Exception as ex:
        print("ERROR: In save_video_raspi.main(): ", ex)


if __name__ == "__main__":
    main()
