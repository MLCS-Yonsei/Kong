
import subprocess 
import multiprocessing as mp
from threading import Thread
from multiprocessing import Pool
from queue import Empty

import time
import datetime
import os
import signal

class StreamingWorker(mp.Process):
    def __init__(self,que,i):
        super(StreamingWorker,self).__init__()
        self.queue = que
        self.i = i

    def run(self):
        i = self.i
        print("Getting Video Source from /dev/video" + str(i))
        video_source = "/dev/video" + str(i)
        
        cmd = ["ffmpeg", 
            "-loglevel", "panic", 
            "-f", "video4linux2", 
            "-r", "30",
            "-i", video_source, 
            #"-c:v", "libx264",
            #"-pix_fmt", "yuv420p", 
            #"-preset", 'ultrafast', 
            #"-g", "20", 
            #"-b:v", "2500k", 
            #"-threads", "0",
            #"-bufsize", "512k",
            "-acodec", "copy", "-f", "ffm", "http://localhost:5800/test.ffm"]

        self.subprocess = subprocess.Popen(cmd)

        while True:
            a = self.subprocess.poll()
            if a is None:
                time.sleep(1)
                try:
                    if self.queue.get(0) == "exit":
                        print("Stopping Video Streaming on /dev/video" + str(i))
                        self.subprocess.terminate()
                        # self.subprocess.wait()
                        break
                    else:
                        pass
                except Empty:
                    pass
        

class VideoStreamer():

    def __init__(self, video_target_device):
        self.jobs = []
        self.queues = []
        self.video_target_device = video_target_device

    def start(self):
        q = mp.Queue()
        job = StreamingWorker(q, self.video_target_device)
        self.queues.append(q)
        self.jobs.append(job)
        job.start()

    def stop(self):
        for q in self.queues:
            q.put("exit")


if __name__ == "__main__":
    pass