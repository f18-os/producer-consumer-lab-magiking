#!/usr/bin/env python3

import threading
import cv2
import os
import numpy as np
import base64

from sys import argv
from time import time, sleep
from threading import Thread, enumerate, Lock
from Queue import Q
# from asyncio import Semaphore
from threading import Semaphore

# globals
global clipFileName, outputDir
outputDir    = 'frames'
clipFileName = 'clip.mp4'

# Extracted frames Queue
global ex_q, ex_lock, ex_empty, ex_full
ex_q = Q()
ex_lock = Lock()
ex_empty = Semaphore(50) # this caps the capacity of our q
ex_full = Semaphore(0) # q is empty to start with (ie no full cells)


# My threads
class ExtractFramesThread(Thread):
    def __init__(self):
        Thread.__init__(self, name="Extract Frames")
    def run(self):
        print(self.name + " running")
        global clipFileName, outputDir
        global ex_q, ex_lock, ex_empty, ex_full
        count = 0
        vidcap = cv2.VideoCapture(clipFileName)

        if not os.path.exists(outputDir):
            print("Output directory {} didn't exist, creating".format(outputDir))
            os.makedirs(outputDir)

        # read one frame
        success,image = vidcap.read()

        print(ex_empty._value)
        ex_empty.acquire()
        ex_lock.acquire()
        print("Reading frame {} {} ".format(count, success))
        ex_q.put(count)
        ex_lock.release()
        ex_full.release()

        while success:
            # write the current frame out as a jpeg image
            cv2.imwrite("{}/frame_{:04d}.jpg".format(outputDir, count), image)   
            success,image = vidcap.read()
            print(ex_empty._value)
            ex_empty.acquire()
            ex_lock.acquire()
            print('Reading frame {}'.format(count))
            print('putting into ex_q')
            ex_q.put(count)
            ex_lock.release()
            ex_full.release()
            count += 1
        # tell next thread that we're done
        print(ex_empty._value)
        ex_empty().acquire()
        ex_lock.acquire()
        print('{} done'.format(self.name))
        ex_q.put(None)
        ex_lock.release()
        ex_full.release()



class GrayscaleThread(Thread):
    def __init__(self):
        Thread.__init__(self, name="Grayscale")
    def run(self):
        print(self.name + " running")
        global outputDir
        global ex_q, ex_lock, ex_empty, ex_full
        count = None

        # get the count
        print(ex_full._value)
        ex_full.acquire()
        ex_lock.acquire()
        count = ex_q.get()
        ex_lock.release()
        ex_empty.release()
        # while inputFrame is not None:
        while True:

            # generate input file name for the next frame
            inFileName = "{}/frame_{:04d}.jpg".format(outputDir, count)

            # load the next frame
            inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)
            if inputFrame is None:
                continue

            print("Converting frame {}".format(count))

            # convert the image to grayscale
            grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)

            # generate output file name
            outFileName = "{}/grayscale_{:04d}.jpg".format(outputDir, count)

            # write output file
            cv2.imwrite(outFileName, grayscaleFrame)

            # get next count
            print(ex_full._value)
            ex_full.acquire()
            ex_lock.acquire()
            count = ex_q.get()
            ex_lock.release()
            ex_empty.release()

            if count == None: # No more frames
                break

        # tell next thread that we're done
        print('{} done'.format(self.name))
        # ex_empty().acquire()
        # try:
        #     ex_lock.acquire()
        #     print('{} done'.format(self.name))
        #     ex_q.put(None)
        #     ex_lock.release()
        # finally:
        #     ex_full.release()


# class DisplayThread(Thread):
#     def __init__(self, iters):
#         Thread.__init__(self, name="DisplayThread")
#     def run(self):
#         print(self.name + " running")
#         global outputDir
#         global ex_q, ex_lock, ex_empty, ex_full
#         frameDelay   = 42       # the answer to everything
#         count = None
#         startTime = time.time()

#         # Generate the filename for the first frame 
#         frameFileName = "{}/grayscale_{:04d}.jpg".format(outputDir, count)

#         # load the frame
#         frame = cv2.imread(frameFileName)

#         # while frame is not None:
#         while True:

#             print("Displaying frame {}".format(count))
#             # Display the frame in a window called "Video"
#             cv2.imshow("Video", frame)

#             # compute the amount of time that has elapsed
#             # while the frame was processed
#             elapsedTime = int((time.time() - startTime) * 1000)
#             print("Time to process frame {} ms".format(elapsedTime))

#             # determine the amount of time to wait, also
#             # make sure we don't go into negative time
#             timeToWait = max(1, frameDelay - elapsedTime)

#             # Wait for 42 ms and check if the user wants to quit
#             if cv2.waitKey(timeToWait) and 0xFF == ord("q"):
#                 break    

#             # get the start time for processing the next frame
#             startTime = time.time()

#             # get the next frame filename
#             count += 1
#             frameFileName = "{}/grayscale_{:04d}.jpg".format(outputDir, count)

#             # Read the next frame file
#             frame = cv2.imread(frameFileName)

#         # make sure we cleanup the windows, otherwise we might end up with a mess
#         cv2.destroyAllWindows()


# Actually start the Threads
thread1 = ExtractFramesThread()
thread2 = GrayscaleThread()
# thread3 = DisplayThread()
thread1.start()
thread2.start()
# thread3.start()
