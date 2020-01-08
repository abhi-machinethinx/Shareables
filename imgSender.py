import imagezmq
import cv2
import sys

def sender(port):
    Sender = imagezmq.ImageSender(connect_to="tcp://*:"+port , REQ_REP=False)
    print("Opened port for receivers:", port)
    
    video_capture = cv2.VideoCapture(0)

    while(video_capture.isOpened()):
        ret, frame = video_capture.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2.imshow('Live', cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        Sender.send_image("Processed", cv2.cvtColor(
            frame, cv2.COLOR_BGR2RGB))

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    sender(sys.argv[1])
