import sys
import os
import cv2
from multiprocessing import Pool                                                
                                                                                                                                                            
                                                                                
def run_process(process):                                                             
    print("Starting Feed for Camera: ", process)
    os.system('python {}'.format(process))                                                                                                                
                                                                                

def main():
    max_devices = 10
    processes = []
    for device in range(max_devices):
        video_capture = cv2.VideoCapture(device)
        if video_capture.isOpened() == True:
            processes.append("camTest.py " + str(device))
            #processes.append("single_instance2.py " + str(device))
            #processes.append("multiprocessing_test.py " + str(device))
        video_capture.release()
        cv2.destroyAllWindows()
    
    print(processes)
    if processes:
        pool = Pool(processes=len(processes))                                                        
        pool.map(run_process, tuple(processes)) 

    
if __name__ == "__main__":
    main()