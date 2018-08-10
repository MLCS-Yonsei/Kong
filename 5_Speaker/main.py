# send_crest_request
import http.client
import csv 
import json
import os.path
import time

from pydub import AudioSegment
import requests

self.audio_path = '/audio/' + self.narr + '/'
        self.method()

def playFile(target_ip, file_path):
    print("Playing...",file_path)
    file_path = str(file_path) + '.wav'
    sound = AudioSegment.from_wav('./audio/' + file_path)
    url = 'http://' + target_ip.split(':')[0] + ':3000/play?path=/audio/' + file_path
    r = requests.get(url)

    return sound.duration_seconds

def send_crest_requset(url, flag, option):
    conn = http.client.HTTPConnection(url, timeout=1)
    try:
        conn.request("GET", "/crest/v1/api")

        res = conn.getresponse()

        data = json.loads(res.read().decode('utf8', "ignore").replace("'", '"'))
        # print("CREST",data)

        return data
    except Exception as e:
        print("CREST_ERROR on send_crest_request:", e)
        data = False
        pass
        
    return data

def get_crest_data(target_ip):
    # 데이터 가져오기
    crest_data = send_crest_requset(target_ip, "crest-monitor", {})

    try:
        gameStates = crest_data['gameStates']

        gameState = gameStates['mGameState']
        sessionState = gameStates['mSessionState']
        raceState = gameStates['mRaceState']

        # print("gameState:",gameState,"/ sessionState:",sessionState,"/ raceState:",raceState, "/ Current IP :", target_ip)

        if gameState == 1 and raceState == 0:
            # Stage 1 : 로비 + 로딩 일부
            return 1, None
        
        elif gameState == 1 and raceState == 1:
            # Stage 2 : 로딩 중
            return 2, None

        elif gameState == 2 and raceState == 1:
            # Stage 2 : 로딩 마무리 중
            return 2, None

        elif gameState == 2 and raceState == 2:
            # Stage 3 : 게임중
            if 'participants' in crest_data:
                current_time = str(datetime.datetime.now())
                gamedata = {'current_time': current_time, 'gamedata': crest_data}
            else:
                gamedata = None

            return 3, gamedata

        elif gameState == 2 and raceState == 3:
            # Stage 4 : 완주
            return 4, None

        elif gameState == 3:
            # Stage 5 : 나가기
            return 5, None

    except Exception as e:
        # print("Crest Error on get_crest_data:",e)
        return False
    
target_ips = ['ubuntu.hwanmoo.kr:8080']
while True:
    for target_ip in target_ips:
        stage, gamedata = get_crest_data(target_ip)

        if stage == 1:
            '''
            로비에서 대기중인 상황.
            crop_detector로 모니터링하다가 사람이 탑승하면 age/gender/color 파악하고 정보 저장.
            파악이 끝나면 기본 안내멘트 재생.
            재생 후 양손이 디텍트되면 게임 스타트 매크로 시작. + 스타트 멘트 재생
            '''
            pass
        elif stage == 2:
            '''
            로딩중 별다른 액션 없음
            '''
            pass
        elif stage == 3:
            '''
            게임중 Speaker 시작
            '''
            pass
        elif stage == 4:
            '''
            완주
            종료 멘트 재생, stage 1로 대기
            '''
        elif stage == 5:
            '''
            나가기
            종료 멘트 재생, stage 1로 대기
            '''
            pass
        else:
            pass