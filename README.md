# Producer Consumer Lab

For this lab you will implement a trivial producer-consumer system using
python threads where all coordination is managed by counting and binary
semaphores for a system of two producers and two consumers. The producers and
consumers will form a simple rendering pipeline using multiple threads. One
thread will read frames from a file, a second thread will take those frames
and convert them to grayscale, and the third thread will display those
frames. The threads will run concurrently.

## File List
### ExtractFrames.py
Extracts a series of frames from the video contained in 'clip.mp4' and saves 
them as jpeg images in sequentially numbered files with the pattern
'frame_xxxx.jpg'.

### ConvertToGrayscale.py
Loads a series for frams from sequentially numbered files with the pattern
'frame_xxxx.jpg', converts the grames to grayscale, and saves them as jpeg
images with the file names 'grayscale_xxxx.jpg'

### DisplayFrames.py
Loads a series of frames sequently from files with the names
'grayscale_xxxx.jpg' and displays them with a 42ms delay.

### ExtractAndDisplay.py
Loads a series of framss from a video contained in 'clip.mp4' and displays 
them with a 42ms delay

## Requirements
* Extract frames from a video file, convert them to grayscale, and display
them in sequence
* You must have three functions
  * One function to extract the frames
  * One function to convert the frames to grayscale
  * One function to display the frames at the original framerate (24fps)
* The functions must each execute within their own python thread
  * The threads will execute concurrently
  * The order threads execute in may not be the same from run to run
* Threads will need to signal that they have completed their task
* Threads must process all frames of the video exactly once
* Frames will be communicated between threads using producer/consumer idioms
  * Producer/consumer quesues will be bounded at ten frames

Note: You may have ancillary objects and method in order to make you're code easer to understand and implement.

# Solution

My solution is in `GrayDisplay.py`

There are two producers-consumer queues used in this project.
One for the counts of the extracted frames,
and one for the counts of the frames converted to grayscale.

For each queue a Lock, and two semaphores were used.
The idioms used to access the queues are as follow.

To bound the Queues, the empty Semaphores are initially set to 10.

For producers:
```
empty_sem.acquire()
lock.acquire()
q.put(count)
lock.release()
full_sem.release()
```

For consumers:
```
full_sem.acquire()
lock.acquire()
count = q.get()
lock.release()
empty_sem.release()
```

The queue implementation used is the one provided by Dr. Freudenthal.
It is in `Queue.py`.

The queues are safeguarded with Locks and Semaphores
so that the three different threads can interact with the queues
safeley.

There is one thread for Extracting the frames,
one for converting them to Grayscale,
and one for displaying the threads.

Each thread only processes each frame once.

# Testing

you can test it with:

```
$ ./test.sh
```
