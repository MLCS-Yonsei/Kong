import sys

sys.path.insert(0, './controllers')
from index import controller

from utils import *

# global Variables
serial = ''
serialActivate = True

player = ''

processes = []
dlProcesses = []
total_video_devices = checkConnectedVideoDevices()
video_target_devices = checkVideoDevices()
crestProcesses = {}
c = controller()

video_recorder = None
recording = False
collecting = False
resolution = "1280x720"

game_flag = {}

streaming = False
streamer = None

hooker = None
hooker_working = False
hooker_detected = False
hooker_position = 0.5
hooker_gender = None
hooker_age = None

record_checker = None