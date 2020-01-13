import sys
import cv2
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
COUNT = 0
RAW_FRAMES_ARR0 = []
RAW_FRAMES_ARR1 = []


# convert string date time to


def convert_to_datetime(time):
    global TODAY
    hour = time[:time.find(":")]
    min = time[3:time.find(":", 3)]
    sec = time[6:time.find(".")]
    return datetime(TODAY.year, TODAY.month, TODAY.day, int(hour), int(min), int(sec))

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
                files = {'file': (SEND_QUEUE[0]["time"]+".mp4", videoFile)}
                data = {"cam_auth_id": CONFIG["cam_auth_id"], "date": str(
                    TODAY.date()), "activityId": SEND_QUEUE[0]["activityId"]}
                res = ReqPost(url=url, data=data, files=files)
                videoFile.close()
                    
                if res.status_code == 200:
                    print("Video ",SEND_QUEUE[0]["path"]," uploaded successfully.")
                    remove(SEND_QUEUE[0]["path"])
                    SEND_QUEUE.pop(0)
                    
            sleep(sleep_len) 
    except Exception as ex:
        print("ERROR: In save_video.send_video():", ex)

# save video


def save_video(index, frame_count, duration, startTime):
    global CONFIG, COUNT, TODAY, SEND_QUEUE, RAW_FRAMES_ARR0, RAW_FRAMES_ARR1

    try:
        COUNT += 1
        print("Save Video thread:", COUNT, " started.")
        print("Video:", round(duration, 3), "Count:", frame_count)

        if index == 0:
            raw_frames = RAW_FRAMES_ARR0
        else:
            raw_frames = RAW_FRAMES_ARR1

        raw_video = None
        t = ""
        activityId = None
        for i, frame in enumerate(raw_frames):
            if i == 0:
                height, width, layers = frame.shape
                fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
                fps = frame_count / duration
                activityId = get_activity(startTime)
                if activityId == None:
                    break
                else:
                    t = str(startTime.time())
                    t = t[:t.find(".")]
                    t = t.replace(":", "-")
                    filename = CONFIG["data"] + \
                        str(TODAY.date()) + "_" + t + "_" + activityId + ".mp4"
                raw_video = cv2.VideoWriter(
                    filename, fourcc, fps, (width, height))

            raw_video.write(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if not raw_video == None:
            SEND_QUEUE.append(
                {"activityId": activityId, "path": filename, "time": t})
            raw_video.release()

        if index == 0:
            del RAW_FRAMES_ARR0[:]
        else:
            del RAW_FRAMES_ARR1[:]

        print("Save Video thread:", COUNT, " finishing.")
    except Exception as ex:
        print("ERROR: In save_video.save_video(): ", ex)

# capture video feed from camera


def startCam(device):
    global CONFIG, RAW_FRAMES_ARR0, RAW_FRAMES_ARR1

    video_capture = None
    try:
        video_capture = cv2.VideoCapture(device)

        print("Video capturing for Camera at index ", device)
        print("Camera FPS: ", video_capture.get(cv2.CAP_PROP_FPS))

        videoTime = CONFIG["video_length"]  # in sec
        frame_count = 0
        index = 0
        timeS = None
        send_thread = None

        while(video_capture.isOpened()):
            ret, frame = video_capture.read()
            if ret == False:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            if frame_count == 0:
                startTime = datetime.now()
                timeS = perf_counter()

            if index == 0:
                RAW_FRAMES_ARR0.append(frame)
            else:
                RAW_FRAMES_ARR1.append(frame)

            frame_count += 1
            timeE = perf_counter()
            if (timeE - timeS) >= videoTime:
                threading.Thread(
                    target=save_video, args=(index, frame_count, (timeE-timeS), startTime, ), daemon=True).start()
                if send_thread == None:
                    send_thread = threading.Thread(
                        target=send_video, daemon=True)
                    send_thread.start()
            
                frame_count = 0
                if index == 0:
                    index = 1
                else:
                    index = 0

            # cv2.imshow('Video'+str(device),
            #               cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as ex:
        print("ERROR: In save_video.startCam(): ", ex)

    if not video_capture == None:
        video_capture.release()
        cv2.destroyAllWindows()


def main(device=0):
    global CONFIG, TODAY, SCHEDULE

    try:
        with open("cam_config.json") as input:
            CONFIG = JLoad(input)
        TODAY = datetime.now()
        # TODAY = datetime(2020,1,13,11,30,58)
        with open(CONFIG["activity"]) as act:
            data = JLoad(act)
            SCHEDULE = data[CONFIG["classId"]][str(TODAY.weekday())]

        startCam(device)
    except Exception as ex:
        print("ERROR: In save_video.main(): ", ex)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(int(sys.argv[1]))
    else:
        main(0)
