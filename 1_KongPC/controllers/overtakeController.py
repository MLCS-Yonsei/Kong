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

class overtakeChecker(mp.Process):

    def __init__(self,que,r,target_ip):
        # [공통] 기본설정
        super(overtakeChecker,self).__init__()
        self.event = mp.Event()
        self.queue = que
        self.r = r
        self.target_ip = target_ip

        self.channels = self.r.pubsub()
        self.channels.subscribe(self.target_ip)

        # Variables
        self.r0_t0 = 0
        self.c = False
        self.status = False

        
    def get_rank(self, data):
        ranks = [info['mRacePosition'] for info in data["participants"]["mParticipantInfo"]]
        return ranks

    def run(self):
        while True:
            time.sleep(0.1)

            message = self.r.hget(self.target_ip,'msg')

            if message:
                data = eval(message)

                gamedata = data['gamedata']
                current_time = data['current_time']

                # Codes
                if "participants" in gamedata:
                    ranks = self.get_rank(gamedata)

                    if len(ranks) > 1:
                        r0_t1 = ranks[0]
                        
                        if self.r0_t0 != 0:
                            
                            if self.r0_t0 > r0_t1:
                                # Overtaked
                                print('추월')
                                self.c = ranks.index(r0_t1 + 1)
                                self.status = True
                            elif self.r0_t0 < r0_t1:
                                # Overtaken
                                print('추월당함')
                                self.c = ranks.index(r0_t1 - 1)
                                self.status = False
                            else:
                                self.c = False

                        if self.c:
                            c_name = gamedata["participants"]["mParticipantInfo"][self.c]["mName"]
                            current_time = str(datetime.datetime.now())

                            result = {}
                            result['current_time'] = current_time
                            result['target_ip'] = self.target_ip
                            result['flag'] = 'overtake'
                            result['data'] = {
                                'status': self.status,
                                'rank': r0_t1
                            }

                            self.r.hset(self.target_ip, 'results', result)

                        self.r0_t0 = r0_t1

    def stop(self):
        self.event.set()
        self.join()
            