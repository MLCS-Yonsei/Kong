from pydub import AudioSegment
from pydub.playback import play
import requests

import random

import time
import os
dir = os.path.dirname(os.path.abspath(__file__))

class audioPlayer():
    def __init__(self, result):
        self.method = getattr(self, result['flag'], lambda: "nothing")

        self.data = result['data']
        self.target_ip = result['target_ip']
        if self.target_ip == 'localhost':
            self.network_flag = False
        else:
            self.network_flag = True

        self.narr = 'ari'
        self.audio_path = '/audio/' + self.narr + '/'
        self.method()

    def playFile(self, file_path):
        print("Playing...",file_path)
        if self.network_flag:
            file_path = self.audio_path + str(file_path) + '.wav'
            # sound = AudioSegment.from_wav(dir + file_path)
            url = 'http://' + self.target_ip.split(':')[0] + ':3000/play?path=' + file_path
            r = requests.get(url)
            # time.sleep(sound.duration_seconds)
        else:
            sound = AudioSegment.from_wav(dir + file_path)
            play(sound)
            # time.sleep(sound.duration_seconds)


    def overtake(self):
        status = self.data['status']

        if status:
            # 추월함
            audio_files =   list(range(2,9)) + \
                            list(range(14,19)) + \
                            list(range(24,28))
            
        else:
            # 추월당함
            audio_files =   list(range(9,14)) + \
                            list(range(19,24)) + \
                            list(range(28,33))

        audio_file = random.choice(audio_files)
        self.playFile(audio_file)


    def chase(self):
        chase = self.data['chasing']
        acc = self.data['acc']
        alone = self.data['alone']
        rank = self.data['rank']

        if alone:
            if rank == 1:
                # 앞선 독주
                audio_files = list(range(164,166))

            elif rank > 1:
                # 뒤쳐진 독주
                audio_files = list(range(166,168))

        else:
            if chase and acc:
                # 잘쫓아감
                audio_files =   list(range(33,41)) + \
                                list(range(55,59)) + \
                                list(range(75,78))
                
            elif chase and (not acc):
                # 잘못쫓아감
                audio_files =   list(range(41,46)) + \
                                list(range(58,61)) + \
                                list(range(70,73))

            elif (not chase) and acc:
                # 잘도망감
                audio_files =   list(range(46,49)) + \
                                list(range(61,64)) + \
                                list(range(73,75))

            elif (not chase) and (not acc):
                # 잘못도망감
                audio_files =   list(range(49,53)) + \
                                list(range(64,70))

        audio_file = random.choice(audio_files)
        self.playFile(audio_file)

    def collision(self):
        crash_state = self.data['crash_state']
        print("Coll ", crash_state)
        if crash_state == 1:
            # 충격 Lv.1
            audio_files =   list(range(78,81)) + \
                            list(range(87,90))
            
        elif crash_state == 2:
            # 충격 Lv.2
            audio_files =   list(range(81,84)) + \
                            list(range(90,92))

        elif crash_state >= 3:
            # 충격 Lv.3
            audio_files =   list(range(84,87)) + \
                            list(range(92,95))
        else:
            audio_files = []

        if len(audio_files) > 0:
            print("AP : Collision")
            audio_file = random.choice(audio_files)
            self.playFile(audio_file)

    def random(self):
        event = self.data['event']

        if event == 'tech':
            # 기술 멘트
            audio_files =   list(range(158,161))
            
        elif event == 'cheer':
            # 격려
            audio_files =   list(range(161,162))

        elif event == 'humor':
            # 유머
            audio_files =   list(range(163,164))

        audio_file = random.choice(audio_files)
        self.playFile(audio_file)

    def lapDistance(self):

        event = self.data['event']

        audio_files = []
        if event == 'start':
            # 시작
            audio_files =   list(range(95,98)) + \
                            list(range(119,123)) + \
                            list(range(141,143))
            
        elif event == 'tunnel':
            # 터널
            audio_files =   list(range(113,115)) + \
                            list(range(135,138)) + \
                            list(range(143,144))
        
        elif event == 'deep_curve':
            # 급한커브
            audio_files =   list(range(108,113)) + \
                            list(range(132,135)) + \
                            list(range(148,150))

        elif event == 'curve':
            # 커브
            audio_files =   list(range(101,108)) + \
                            list(range(126,132)) + \
                            list(range(144,148))

        elif event == 'straight':
            # 직선
            audio_files =   list(range(115,119)) + \
                            list(range(138,141)) + \
                            list(range(155,158))

        elif event == 'finish':
            # 종료
            audio_files =   list(range(98,101)) + \
                            list(range(123,126)) + \
                            list(range(153,155))

        elif event == 'section_1':
            # 1구간
            audio_files =   list(range(150,151))

        elif event == 'section_2':
            # 2구간
            audio_files =   list(range(151,152))

        elif event == 'section_3':
            # 3구간
            audio_files =   list(range(152,153))

        elif event == 'r_finish':
            # 종료 후
            audio_files =   list(range(168,177))

        if len(audio_files) > 0:
            audio_file = random.choice(audio_files)
            self.playFile(audio_file)

            

