import time
import sys
import cv2

def camTest(device = 0):
    video_capture = cv2.VideoCapture(device)
    print("Video capturing for CAM:", device)
    print("FPS:", video_capture.get(cv2.CAP_PROP_FPS))
    
    while(video_capture.isOpened()):
        ret, frame = video_capture.read()
        if ret == False:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        cv2.imshow('CAM'+str(device),
                       cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        camTest(int(sys.argv[1]))
    else:
        camTest(0)
