import sys
import stat
import os
import glob
sys.path.insert(0, './bin')
sys.path.insert(0, './config')
import globalVariables as gv

sys.path.insert(0, './bin/age_gender')
from age_gender_main import *
import tensorflow as tf

import multiprocessing
from threading import Thread

# send_crest_request
import http.client
import csv 
import json
import os.path

import threading
import datetime
import redis

import time 

import sqlite3
import cv2

from videoRecorder import VideoRecorder
from videoStreamer import VideoStreamer
from audioPlayer import audioPlayer

import serial
import serial.tools.list_ports

from pcars_stream.src.pcars.stream import PCarsStreamReceiver

def data_collect_start():
    # Checking Available Simulators
    sims = checkSims()   

    # Getting Pcars Data
    gv.crestProcesses = getPcarsData(sims,gv.r,gv.crestProcesses)
    #gv.record_checker = crest_check_record_mp()
    # Refresh App Status
    gv.app_status = checkAppStatus()
    
def data_collect_stop():
    gv.crestProcesses = stopGettingPcarsData(gv.crestProcesses)
    # if gv.record_checker != None:
    #     gv.record_checker.terminate()


def hooker_age_gender_estimating_sess(img, class_type, files, tgtdir):
    config = tf.ConfigProto(allow_soft_placement=True,device_count={'GPU': 0})
    config.gpu_options.allow_growth = True
    with tf.Session(config=config) as sess:
        GENDER_LIST =['M','F']
        AGE_LIST = ['(0, 3)','(4, 7)','(8, 13)','(14, 20)','(21, 33)','(34, 45)','(46, 59)','(60, 100)']

        label_list = AGE_LIST if class_type == 'age' else GENDER_LIST
        nlabels = len(label_list)

        model_fn = select_model('default')

        with tf.device('/cpu:0'):
            
            images = tf.placeholder(tf.float32, [None, RESIZE_FINAL, RESIZE_FINAL, 3])
            logits = model_fn(nlabels, images, 1, False)
            init = tf.global_variables_initializer()
            
            requested_step = None # FLAGS.requested_step if FLAGS.requested_step else None
        
            if class_type == 'gender':
                checkpoint_path = '%s' % ('./bin/age_gender/2_GEN_fold/gen_test_fold_is_WKFD/run-22588')
            else:
                checkpoint_path = '%s' % ('./bin/age_gender/1_AGE_fold/age_test_fold_is_WKFD/run-12870')

            model_checkpoint_path, global_step = get_checkpoint(checkpoint_path, requested_step, 'checkpoint')
            
            saver = tf.train.Saver()
            saver.restore(sess, model_checkpoint_path)
                        
            softmax_output = tf.nn.softmax(logits)

            coder = ImageCoder()

            if (len(files)>0):
                best_choices = age_gender_main(sess, img, label_list, softmax_output, coder, images, files, tgtdir)
                parse_estimation(best_choices)

            while True:
                time.sleep(0.1)

                if gv.hooker_working == False:
                    files = []
                    face_files, img, tgtdir = hooker_capture()
                    files += face_files

                    if (len(files)>0):
                        best_choices = age_gender_main(sess, img, label_list, softmax_output, coder, images, [files[0]], tgtdir)
                        parse_estimation(best_choices)


def robot_controller(position):
    gv.hooker_position = position
    # 로봇 이동 코드 삽입
    gv.hooker_working = True

def parse_estimation(result):
    # 요일 specific 멘트
    if len(result[0][0]) == 1:
        gv.hooker_gender = result[0][0]
    else:
        _age = eval(result[0][0])[0]
        
        if _age<20:
            _age_type = 0
        elif _age>=20 and _age<45:
            _age_type = 1
        elif _age>=45:
            _age_type = 2

        gv.hooker_age = _age_type

def hooker_capture():
    cap = cv2.VideoCapture(1)
    
    _, img = cap.read()
    height, width = img.shape[:2]

    w1 = int(width/2)
    w2 = int(width)
    h1 = int(height/2)
    h2 = int(height)
    quadrant = 0
    if quadrant == 1:
        img = img[0:h1,w1:w2]
    elif quadrant == 2:
        img = img[int(height/2):height,0:int(width/2)]
    elif quadrant == 3:
        img = img[int(height/2):height,0:int(width/2)]
    elif quadrant == 4:
        img = img[0:int(height/2),int(width/2):width]


    ch1 = int(0.1 * height)
    ch2 = int(0.8 * height)
    cw1 = int(0.2 * width)
    cw2 = int(0.8 * width)

    cc1 = int(0.2 * (cw2 - cw1))
    cc2 = int((1 - 0.3) * (cw2 - cw1))
    img = img[ch1:ch2,cw1:cw2]

    files = []
    face_detect = face_detection_model('dlib', './bin/age_gender/Model/shape_predictor_68_face_landmarks.dat')
    faces, face_files, rectangles, tgtdir = face_detect.run(img)
    if len(faces) > 0:
        btm = faces[0].bottom()
        x_center = faces[0].left() + int((faces[0].right() - faces[0].left())/2)

        pts0 = np.float32([[btm],[x_center],[1]])
        pts1 = np.float32([[cc1,0],[0,ch2-ch1],[cc2,0],[cw2-cw1,ch2-ch1]])
        pts2 = np.float32([[0,0],[0,ch2-ch1],[cw2-cw1,0],[cw2-cw1,ch2-ch1]])

        M = cv2.getPerspectiveTransform(pts1, pts2)

        # 대상체로 이동
        pts3 = np.matmul(M,pts0)

        robot_controller(pts3[0][0]/(cw2-cw1))

    return face_files, img, tgtdir

def hooker():
    files = []
    face_files, img, tgtdir = hooker_capture()
    files += face_files

    threads = []
    for _c in ['gender','age']:
        _t = Thread(target=hooker_age_gender_estimating_sess, args=(img,_c, [files[0]], tgtdir))
        _t.start()
        threads.append(_t)

    for _t in threads:
        _t.join()

def hooker_start():
    print("Starting hooker")
    mp = multiprocessing.Process(target=hooker, args=())
    mp.start()
    
    return mp

def hooker_stop():
    print("Stopping hooker")
    if gv.hooker is not None:
        gv.hooker.terminate()
        gv.hooker.join() 
        gv.hooker = None

    # Update App Status
    app_status = checkAppStatus()
    app_status["hooker"] = False
    updateAppStatus(app_status)


def streamer(dev):
    pass

def streaming_start(dev):
    if gv.recording == True:
        print("Can't stream when recording")
    else:
        print("Start Streaming on",dev)
        gv.streamer = VideoStreamer(dev)
        gv.streamer.start()
        gv.streaming = True

def streaming_stop():
    print(gv.streamer)
    if gv.streamer != None:
        gv.streamer.stop()
        gv.streamer = None
        gv.streaming = False

def record_start():
    if gv.streamer != None or gv.streaming == True:
        streaming_stop()
        gv.streaming = False

    current_time = datetime.datetime.now()
    print("Total video devices:",gv.total_video_devices)
    print("Target video devices:",gv.video_target_devices)
    gv.video_recorder = VideoRecorder(gv.video_target_devices, gv.resolution, current_time)
    gv.video_recorder.start()
    gv.recording = True

    # Update App Status
    app_status = checkAppStatus()
    app_status["recording"] = gv.recording
    updateAppStatus(app_status)

    message = "Recording Started!"
    gv.r.publish('message', message)
    print(message)

def record_stop():
    if gv.video_recorder != None:
        gv.video_recorder.stop()

    gv.recording = False

    app_status = checkAppStatus()
    app_status["recording"] = gv.recording
    updateAppStatus(app_status)

    message = "Recording Stopped!"
    gv.r.publish('message', message)
    print(message)

def age_gender_estimating_sess(img, class_type, files, tgtdir):
    config = tf.ConfigProto(allow_soft_placement=True,device_count={'GPU': 0})
    config.gpu_options.allow_growth = True
    with tf.Session(config=config) as sess:
        GENDER_LIST =['M','F']
        AGE_LIST = ['(0, 3)','(4, 7)','(8, 13)','(14, 20)','(21, 33)','(34, 45)','(46, 59)','(60, 100)']

        label_list = AGE_LIST if class_type == 'age' else GENDER_LIST
        nlabels = len(label_list)

        model_fn = select_model('default')

        with tf.device('/cpu:0'):
            
            images = tf.placeholder(tf.float32, [None, RESIZE_FINAL, RESIZE_FINAL, 3])
            logits = model_fn(nlabels, images, 1, False)
            init = tf.global_variables_initializer()
            
            requested_step = None # FLAGS.requested_step if FLAGS.requested_step else None
        
            if class_type == 'gender':
                checkpoint_path = '%s' % ('./bin/age_gender/2_GEN_fold/gen_test_fold_is_WKFD/run-22588')
            else:
                checkpoint_path = '%s' % ('./bin/age_gender/1_AGE_fold/age_test_fold_is_WKFD/run-12870')

            model_checkpoint_path, global_step = get_checkpoint(checkpoint_path, requested_step, 'checkpoint')
            
            saver = tf.train.Saver()
            saver.restore(sess, model_checkpoint_path)
                        
            softmax_output = tf.nn.softmax(logits)

            coder = ImageCoder()

            # while True:
            time.sleep(0.1)

            age_gender_main(sess, img, label_list, softmax_output, coder, images, files, tgtdir)

def age_gender_estimator(target_device):
    print('target_devie:',target_device)
    cap = cv2.VideoCapture(int(target_device))
    print(cap.isOpened)
    _, img = cap.read()
    print(img)

    if img != None:
        files = []
        face_detect = face_detection_model('dlib', './bin/age_gender/Model/shape_predictor_68_face_landmarks.dat')
        faces, face_files, rectangles, tgtdir = face_detect.run(img)
        files += face_files

        threads = []
        for _c in ['gender','age']:
            _t = Thread(target=age_gender_estimating_sess, args=(img,_c, files, tgtdir))
            _t.start()
            threads.append(_t)

        for _t in threads:
            _t.join()

def age_gender_mp(target_device):
    mp = multiprocessing.Process(target=age_gender_estimator, args=(str(target_device)))
    mp.start()
    
    return mp

def get_age_gender(target_devices, dlProcesses):
    # Update App Status
    print("Get Age Gender")
    app_status = checkAppStatus()

    if app_status["deepLearning"]["ageGender"] == True:
        dlProcesses = stop_getting_age_gender(dlProcesses)

    app_status["deepLearning"]["ageGender"] = True
    updateAppStatus(app_status)
    
    for _t in target_devices:
        print("Init Video device at",_t)
        _mp = age_gender_mp(_t)
        dlProcesses.append(_mp)

    return dlProcesses

def stop_getting_age_gender(dlProcesses):
    for _mp in dlProcesses:
        _mp.terminate()
        _mp.join()  

    dlProcesses = []

    # Update App Status
    app_status = checkAppStatus()
    app_status["deepLearning"]["ageGender"] = False
    updateAppStatus(app_status)

    return dlProcesses
            
def dl_start():
    print('Deep Learning Based Speaker Start')
    gv.dlProcesses = get_age_gender(gv.video_target_devices, gv.dlProcesses)

def dl_stop():
    print('Deep Learning Based Speaker Stop')
    gv.dlProcesses = stop_getting_age_gender(gv.dlProcesses)

def checkAppStatus():
    # DB for config
    conn = sqlite3.connect("./config/db/test.db")
    cur = conn.cursor()

    # Getting Simulator info
    cur.execute("select * from common where key = 'app_status'")
    results = cur.fetchall()
    
    if len(results) == 0:
        app_status = {}
        app_status["ruleBase"]["overtake"] = False
        app_status["ruleBase"]["chase"] = False
        app_status["ruleBase"]["mapDistance"] = False
        app_status["deepLearning"]["ageGender"] = False
        app_status["dataCollect"] = False
        app_status["pcarsData"] = False
        app_status["recording"] = False
        app_status["serialActivate"] = True
        app_status["hooker"] = False

        _as = json.dumps(app_status)

        cur.execute("insert into common(key, value) values ('app_status', ?)", (_as,))
        conn.commit()
    else:
        app_status =  json.loads(results[0][1])

    # Connection 닫기
    conn.close()

    return app_status

def checkConnectedVideoDevices():
    # Check for devices
    total_video_devices = []
    for i in range(10):
        path = "/dev/video" + str(i)
        if os.path.exists(path):
            total_video_devices.append(i)

    return total_video_devices

def checkVideoDevices():
    gv.total_video_devices = checkConnectedVideoDevices()

    # DB for config
    conn = sqlite3.connect("./config/db/test.db")
    cur = conn.cursor()

    # Getting Simulator info
    cur.execute("select * from common where key = 'video_devices'")
    results = cur.fetchall()
    
    if len(results) == 0:
        video_devices = gv.total_video_devices

        _vd = json.dumps(video_devices)

        cur.execute("insert into common(key, value) values ('video_devices', ?)", (_vd,))
        conn.commit()
    else:
        video_devices =  json.loads(results[0][1])

    if len(gv.total_video_devices) < len(video_devices):
        video_devices = gv.total_video_devices
        updateVideoDevices(video_devices)

    # Connection 닫기
    conn.close()

    return video_devices

def getVideoList():
    return glob.glob("./data/video/*.mp4")

def updateAppStatus(app_status):
    # DB for config
    conn = sqlite3.connect("./config/db/test.db")
    cur = conn.cursor()

    # print("App status Updated", app_status)
    # Update query
    _as = json.dumps(app_status)
    cur.execute("update common set value = ? where key = 'app_status'", (_as,))

    conn.commit()
    conn.close()

    return True

def updateVideoDevices(video_devices):
    # DB for config
    conn = sqlite3.connect("./config/db/test.db")
    cur = conn.cursor()

    print("Video Devices Updated", video_devices)
    # Update query
    _vd = json.dumps(video_devices)
    cur.execute("update common set value = ? where key = 'video_devices'", (_vd,))

    conn.commit()
    conn.close()

    return True


def rb_start():
    print("Activating Rule Based Speaker")
    # Checking Available Simulators
    sims = checkSims()   

    # Getting Pcars Data
    gv.crestProcesses = getPcarsData(sims,gv.r,gv.crestProcesses)
    
    # Refresh App Status
    gv.app_status = checkAppStatus()
    
    # Init Audio Player
    # gv.player = multiprocessing.Process(target=aPlayer, args=(gv.r, sims))
    # gv.player.start()
    gv.player = aPlayer_start(gv.r, sims)

    # Storing Processes
    gv.processes = []
    for sim in sims:
        if gv.app_status["ruleBase"]["overtake"]:
            _ot = gv.c.checkOvertake(gv.r,sim[0])
            gv.processes.append(_ot)

            # collision checker
            _co = gv.c.collisionChecker(gv.r,sim[0])
            gv.processes.append(_co)

        if gv.app_status["ruleBase"]["chase"]:
            _cc = gv.c.chaseChecker(gv.r,sim[0])
            gv.processes.append(_cc)

        if gv.app_status["ruleBase"]["mapDistance"]:
            _ld = gv.c.lapDistanceChecker(gv.r,sim[0])
            gv.processes.append(_ld)

def serial_listener():
    # Scan for arduino ports
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "Arduino" in p[1]:
            port = p[0]
            break

    try:
        ard = serial(port,9600,timeout=5)
        time.sleep(2)

        while True:
            if gv.app_status["serialActivate"] == True:
                # Send Signal
                ard.write(b"get_button_data")
                time.sleep(0.3)
                msg = ard.readline().decode("utf-8")

                # parse msg..
                ctl = msg
                if ctl[0] == "1":
                    if ctl[1] == "1":
                        rb_start()
                    else:
                        rb_stop()
                
                if ctl[0] == "1":
                    rb_stop()
            else:
                time.sleep(5)
    except:
        print("No Arduino Connected")
        


def serial_listener_start():
    print("Listening to serial Ports")
    gv.serial = multiprocessing.Process(target=serial_listener, args=())
    gv.serial.start()

def serial_listener_stop():
    print("Stopping Listening to serial Ports")
    gv.serial.stop()


def rb_stop():
    print("Stopping Rule Based Speaker")
    # Stopping Processes
    for _p in gv.processes:
        _p.terminate()
        _p.join()

    # Stopping Audio Player
    try:
        # gv.player.terminate()
        # gv.player.join()
        aPlayer_stop()
    except:
        pass

    # Stop Getting Process
    gv.crestProcesses = stopGettingPcarsData(gv.crestProcesses)

    # Refresh App Status
    gv.app_status = checkAppStatus()

def checkSims():
    # DB for config
    conn = sqlite3.connect("./config/db/test.db")
    cur = conn.cursor()

    # Getting Simulator info
    cur.execute("select * from simulators")
    _sims = cur.fetchall()
      
    # Connection 닫기
    conn.close()

    sims = []
    for sim in _sims:
        r = send_crest_requset(sim[0], 'crest-monitor', {})

        if r != False:
            sims.append(sim)

    return sims

def getPcarsData(sims, r, crestProcesses):
    # Update App Status
    app_status = checkAppStatus()

    if app_status["pcarsData"] == True:
        stopGettingPcarsData(crestProcesses)
    
    app_status["pcarsData"] = True
    updateAppStatus(app_status)

    for sim in sims:
        crestProcess = crest_data_mp(sim[0], r)
        crestProcesses[sim[0]] = crestProcess

    return crestProcesses

def stopGettingPcarsData(crestProcesses):
    for ip in crestProcesses:
        crestProcess = crestProcesses[ip]
        crestProcess.terminate()
        crestProcess.join()  

    crestProcesses = {}  

    # Update App Status
    app_status = checkAppStatus()
    app_status["pcarsData"] = False
    updateAppStatus(app_status)

    return crestProcesses
'''
def aPlayer(r, sims):
    channels = r.pubsub()
    
    # 여러 채널이 가능한지 추가 확인 필요
    # 여러 시뮬레이터가 results 채널로 모두 송신 -> 수신되는 results 값 안에 target_ip 있음.
    for sim in sims:
        channels.subscribe(sim[0])

    # print(msg_buffer)
    while True:
        for sim in sims:
            message = r.hget(sim[0],'results')
            r.hdel(sim[0],'results')
            
            if message:
                print("D1",sim[0], message)
                result = eval(message)
                
                msg_time = datetime.datetime.strptime(result['current_time'], '%Y-%m-%d %H:%M:%S.%f')
                ref_time = datetime.datetime.now() - datetime.timedelta(seconds=10)
                # print(msg_time,ref_time)
                if msg_time > ref_time:
                    # result = {key.decode(): value.decode() for (key, value) in message.items()}
                    
                    # 2초보다 오래된 메세지 제거
                    # print('aPlayer',result)
                    # print('#######')
                    # print(msg_buffer[result['target_ip']])

                    t1 = threading.Thread(target=aPlayerThread, args=(result,))
                    t1.daemon = True 
                    t1.start()

                    # 오디오 겹치지 않게 여기에 sleep 필요할수도.. 그러면 초 정보 가져와야함
                    # 일단은 7초동안 sleep
                    
        # time.sleep(7)
'''
def aPlayerThread(result):
    p = audioPlayer(result)

def aPlayerMP(r,sim):
    while True:
        message = r.hget(sim[0],'results')
        
        if message:
            r.hdel(sim[0],'results')
            
            result = eval(message)
            
            msg_time = datetime.datetime.strptime(result['current_time'], '%Y-%m-%d %H:%M:%S.%f')
            ref_time = datetime.datetime.now() - datetime.timedelta(seconds=10)
            # print(msg_time,ref_time)
            if msg_time > ref_time:
                print("D1",sim[0], message)
                # result = {key.decode(): value.decode() for (key, value) in message.items()}
                
                # 2초보다 오래된 메세지 제거
                # print(msg_buffer[result['target_ip']])

                t1 = threading.Thread(target=aPlayerThread, args=(result,))
                t1.daemon = True 
                t1.start()

                time.sleep(5)

                t1.join()
                # 오디오 겹치지 않게 여기에 sleep 필요할수도.. 그러면 초 정보 가져와야함
                # 일단은 7초동안 sleep

def aPlayer_start(r, sims):
    aPlayer_stop()
    
    print("Starting aPlayer")

    channels = r.pubsub()
    
    # 여러 채널이 가능한지 추가 확인 필요
    # 여러 시뮬레이터가 results 채널로 모두 송신 -> 수신되는 results 값 안에 target_ip 있음.
    player = []
    for sim in sims:
        channels.subscribe(sim[0])

        mp = multiprocessing.Process(target=aPlayerMP, args=(r,sim,))
        mp.start()

        player.append(mp)
    
    return player

def aPlayer_stop():
    print("Stopping aPlayer")
    if gv.player is not None:
        for mp in gv.player:
            mp.terminate()
            mp.join() 

        gv.player = None


def interrupt():
    stopGettingPcarsData(gv.crestProcesses)

    try:
        gv.player.terminate()
        gv.player.join()
    except:
        pass

    try:
        for _p in gv.processes:
            _p.terminate()
            _p.join()
    except:
        pass

    try:
        for _p in gv.dlProcesses:
            _p.terminate()
            _p.join()
    except:
        pass

    gv.app_status["ruleBase"]["overtake"] = False
    gv.app_status["ruleBase"]["chase"] = False
    gv.app_status["ruleBase"]["mapDistance"] = False
    gv.app_status["deepLearning"]["ageGender"] = False
    gv.app_status["dataCollect"] = False
    gv.app_status["pcarsData"] = False
    gv.app_status["recording"] = False
    gv.app_status["serialActivate"] = True
    gv.app_status["hooker"] = False

    updateAppStatus(gv.app_status)
    serial_listener_stop()

class PCarsListener(object):
    def __init__(self):
        self.data = None

    def handlePacket(self, data):
        # You probably want to do something more exciting here
        # You probably also want to switch on data.packetType
        # See listings in packet.py for packet types and available fields for each
        # print(data._data)
        self.data = data._data
        # print(self.data)

def send_crest_requset(url, flag, option):
    conn = http.client.HTTPConnection(url, timeout=1)
    try:
        conn.request("GET", "/crest/v1/api")

        res = conn.getresponse()

        data = json.loads(res.read().decode('utf8', "ignore").replace("'", '"'))
        # print("CREST",data)

        gv.gameState = data["gameStates"]["mGameState"]
        if data["gameStates"]["mGameState"] > 1:
            if flag == 'crest-monitor':
                return data
    except Exception as e:
        # print("CREST_ERROR on send_crest_request:", e)
        data = False
        pass
        
    return data

def check_to_record():

    time.sleep(0.1)
    if gv.recording == False:
        _f = False
        
        for target_ip, flag in gv.game_flag.items():
            if flag == True:
                _f = True
                
        
        if _f == True:
            gv.video_target_devices = checkVideoDevices()
            record_start()
            gv.recording = True
    elif gv.recording == True:
        _f = True
        for target_ip, flag in gv.game_flag.items():
            if flag == True:
                _f = False

        if _f == True:
            record_stop()
            gv.recording = False

def get_crest_data(target_ip, r):
    while True:
        # 데이터 가져오기
        time.sleep(0.1)
        crest_data = send_crest_requset(target_ip, "crest-monitor", {})
        # print("GET CREST DATA")
        try:
            gameState = crest_data['gameStates']['mGameState']
            # print("gameState",gameState)
            if gameState > 1 and 'participants' in crest_data:
                if 'mParticipantInfo' in crest_data["participants"]:
                    # 게임 플레이중
                    gv.game_flag[target_ip] = True
                    # check_to_record()

                    current_time = str(datetime.datetime.now())
                    gamedata = {'current_time': current_time, 'gamedata': crest_data}
                    # print(current_time)
                    conn = sqlite3.connect("./config/db/test.db")
                    cur = conn.cursor()

                    _js_game_data = json.dumps(gamedata)

                    cur.execute("insert into game_data(target_ip, game_data, current_time) values (?, ?, ?)", (target_ip,_js_game_data,current_time,))
                    conn.commit()

                    conn.close()

                    # time.sleep(0.1)
                    r.hdel(target_ip,'msg')
                    r.hset(target_ip, 'msg', gamedata)

            else:
            # 플레이 종료
                # print("Off game", target_ip)
                gv.game_flag[target_ip] = False
                # check_to_record()

        except Exception as e:
            # print("Crest Error on get_crest_data:",e)
            pass
    
def crest_check_record_mp():
    print("Record Checker Start")
    record_checker = multiprocessing.Process(target=check_to_record, args=())
    record_checker.start()

    return record_checker

def crest_data_mp(target_ip, r):
    crest = multiprocessing.Process(target=get_crest_data, args=(target_ip, r))
    crest.start()
    print(crest)
    return crest

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")
