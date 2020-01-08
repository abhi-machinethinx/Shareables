import imagezmq
import cv2
import sys

RECEIVER = None

def startReceiving():
    global RECEIVER
    while True:
        info, frame = RECEIVER.recv_image()
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2.imshow(info, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    cv2.destroyAllWindows()

        
def receiver(ip_port):
    global RECEIVER
    print("Establishing connection to", ip_port)
    RECEIVER = imagezmq.ImageHub(open_port='tcp://'+ip_port, REQ_REP = False)
    startReceiving()

if __name__=="__main__":
    receiver(sys.argv[1])