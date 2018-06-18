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

        
        self.method()

    def playFile(self, file_path):
        print("Playing...",file_path)
        if self.network_flag:
            sound = AudioSegment.from_wav(dir + file_path)
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
            audio_files = ['/audio/nayoung/overtake/c-01.wav','/audio/nayoung/overtake/c-02.wav',
            '/audio/nayoung/overtake/c-03.wav','/audio/nayoung/overtake/c-04.wav','/audio/nayoung/overtake/c-05.wav']
            
        else:
            # 추월당함
            audio_files = ['/audio/nayoung/overtaken/c-06.wav','/audio/nayoung/overtaken/c-07.wav',
            '/audio/nayoung/overtaken/c-08.wav','/audio/nayoung/overtaken/c-09.wav','/audio/nayoung/overtaken/c-10.wav']

        audio_file = random.choice(audio_files)
        self.playFile(audio_file)


    def chase(self):
        chase = self.data['chasing']
        acc = self.data['acc']

        if chase and acc:
            # 잘쫓아감
            audio_files = ['/audio/nayoung/chase_good/c-11.wav','/audio/nayoung/chase_good/c-12.wav',
            '/audio/nayoung/chase_good/c-13.wav','/audio/nayoung/chase_good/c-14.wav','/audio/nayoung/chase_good/c-15.wav',
            '/audio/nayoung/chase_good/c-16.wav','/audio/nayoung/chase_good/c-17.wav']
            
        elif chase and (not acc):
            # 잘못쫓아감
            audio_files = ['/audio/nayoung/chase_bad/c-18.wav','/audio/nayoung/chase_bad/c-19.wav',
            '/audio/nayoung/chase_bad/c-20.wav','/audio/nayoung/chase_bad/c-21.wav','/audio/nayoung/chase_bad/c-22.wav',
            '/audio/nayoung/chase_bad/c-23.wav','/audio/nayoung/chase_bad/c-24.wav']

        elif (not chase) and acc:
            # 잘도망감
            audio_files = ['/audio/nayoung/escape_good/c-25.wav','/audio/nayoung/escape_good/c-26.wav',
            '/audio/nayoung/escape_good/c-27.wav']

        elif (not chase) and (not acc):
            # 잘못도망감
            audio_files = ['/audio/nayoung/escape_bad/c-28.wav','/audio/nayoung/escape_bad/c-29.wav',
            '/audio/nayoung/escape_bad/c-30.wav','/audio/nayoung/escape_bad/c-31.wav']

        audio_file = random.choice(audio_files)
        self.playFile(audio_file)

    def lapDistance(self):

        event = self.data['event']

        if event == 'start':
            # 시작
            audio_files = ['/audio/nayoung/start/c-34.wav','/audio/nayoung/start/c-35.wav','/audio/nayoung/start/c-36.wav']
            
        elif event == 'tunnel':
            # 터널
            audio_files = ['/audio/nayoung/tunnel/c-52.wav','/audio/nayoung/tunnel/c-53.wav']
        
        elif event == 'deep_curve':
            # 급한커브
            audio_files = ['/audio/nayoung/deep_curve/c-47.wav','/audio/nayoung/deep_curve/c-48.wav',
            '/audio/nayoung/deep_curve/c-49.wav','/audio/nayoung/deep_curve/c-50.wav','/audio/nayoung/deep_curve/c-51.wav']

        elif event == 'curve':
            # 커브
            audio_files = ['/audio/nayoung/curve/c-40.wav','/audio/nayoung/curve/c-41.wav','/audio/nayoung/curve/c-42.wav',
            '/audio/nayoung/curve/c-43.wav','/audio/nayoung/curve/c-44.wav','/audio/nayoung/curve/c-45.wav',
            '/audio/nayoung/curve/c-46.wav']

        elif event == 'straight':
            # 직선
            audio_files = ['/audio/nayoung/straight/c-54.wav','/audio/nayoung/straight/c-55.wav',
            '/audio/nayoung/straight/c-56.wav','/audio/nayoung/straight/c-57.wav']

        elif event == 'finish':
            # 종료
            audio_files = ['/audio/nayoung/finish/c-37.wav','/audio/nayoung/finish/c-38.wav',
            '/audio/nayoung/finish/c-39.wav']

        audio_file = random.choice(audio_files)
        self.playFile(audio_file)

