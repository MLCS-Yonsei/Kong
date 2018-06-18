import subprocess 
import multiprocessing as mp
from threading import Thread
from multiprocessing import Pool
from queue import Empty

import time
import datetime
import os
import signal

import redis

class collisionChecker(mp.Process):

    def __init__(self,que,r,target_ip):
        # [공통] 기본설정
        super(collisionChecker,self).__init__()
        self.queue = que
        self.r = r
        self.target_ip = target_ip

        self.channels = self.r.pubsub()
        self.channels.subscribe(self.target_ip)

        # Variables


    def run(self):
        while True:
            message = self.r.hget(self.target_ip,'msg')

            if message:
                data = eval(message)

                gamedata = data['gamedata']
                current_time = data['current_time']
                
                # Codes
                current_time = str(datetime.datetime.now())
                
                result = {}
                result['current_time'] = current_time      
                result['target_ip'] = self.target_ip
                result['flag'] = 'collision'

                '''
                지금 도로를 이탈하였는지 확인하고, (terrein 부분 제거?)
                전체 velocity가 특정 값으로 내려오면 행동불능 상태로 판명
                
                아니면 그냥
                crash state 발생했을때
                그 레벨 (1,2,3)에 대해 강도 멘트. 2는 거의 없고 1 : 가벼운 충돌, 3 : 강력한 충돌 위주로.

                mworldpoisition -> 변화량 측정해서 lap_distance의 변화량의 어느 정도 보다 적으면 후진이나 차빼기 멘트
                '''
                collision = gamedata["wheelsAndTyres"]["mTerrain"][0] != 0 and gamedata["wheelsAndTyres"]["mTerrain"][2] !=0
                velocity = sum( i*i for i in gamedata["motionAndDeviceRelated"]["mLocalVelocity"])

                if collision and velocity < 1.5 :
                    print('collision')
                    result['data'] = {
                    'collision' : True
                }
                

                self.r.hset(self.target_ip, 'results', result)

            time.sleep(0.1)
                
                