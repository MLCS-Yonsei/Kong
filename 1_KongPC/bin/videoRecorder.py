
import subprocess 
import multiprocessing as mp
from threading import Thread
from multiprocessing import Pool
from queue import Empty

import time
import datetime
import os
import signal

class RecordWorker(mp.Process):
    def __init__(self,que,i,resolution,record_time):
        super(RecordWorker,self).__init__()
        self.queue = que
        self.i = i
        self.resolution = resolution
        if isinstance(record_time, datetime.datetime):
            self.record_time = record_time.strftime('%Y%m%d%H%M%S')
        else:
            self.record_time = record_time

    def run(self):
        i = self.i
        print("Getting Video Source from /dev/video" + str(i))
        video_source = "/dev/video" + str(i)
        
        print("Saving in video/" + self.record_time + "_" + str(i))
        cmd = ["ffmpeg", "-y", 
            "-loglevel", "panic", 
            "-f", "video4linux2", 
            "-thread_queue_size", "512", 
            "-i", video_source, 
            # "-f", "alsa", 
            #"-thread_queue_size", "512", 
            #"-i", "hw:"+ str(i+2) +",0", 
            "-vcodec", "libx264",
            "-pix_fmt", "yuv420p", 
            "-s", self.resolution, 
            "-r", "30", 
            "-aspect", "16:9", 
            #"-acodec", "libmp3lame", 
            #"-b:a", "128k", 
            #"-channels", "2", 
            #"-ar", "48000", 
            "-an", "./data/video/" + self.record_time + "_" + str(i) + ".mp4"]
        self.subprocess = subprocess.Popen(cmd)

        while True:
            a = self.subprocess.poll()
            if a is None:
                time.sleep(1)
                try:
                    if self.queue.get(0) == "exit":
                        print("Stopping Video Recording from /dev/video" + str(i))
                        self.subprocess.terminate()
                        # self.subprocess.wait()
                        break
                    else:
                        pass
                except Empty:
                    pass
                # print("run")
            # else:
            #     print("exiting")
        

class VideoRecorder():

    def __init__(self, video_target_devices, resolution, record_time):
        self.jobs = []
        self.queues = []
        self.video_target_devices = video_target_devices
        self.resolution = resolution
        self.record_time = record_time

    def start(self):
        for i in self.video_target_devices:
            q = mp.Queue()
            job = RecordWorker(q, i, self.resolution, self.record_time)
            self.queues.append(q)
            self.jobs.append(job)
            job.start()

    def stop(self):
        for q in self.queues:
            q.put("exit")


if __name__ == "__main__":
    current_time = datetime.datetime.now()

    video_target_devices = [0]
    resolution = "1280x720"

    vr = VideoRecorder(video_target_devices, resolution, current_time)
    vr.start()
    # wait for a while and then kill jobs
    time.sleep(6)
    vr.stop()

    time.sleep(2)