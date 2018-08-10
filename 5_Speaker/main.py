# send_crest_request
from utils import *
from crop_detection import Detector

import time
from threading import Thread


target_ips = ['ubuntu.hwanmoo.kr:8080']

variables = {}
for target_ip in target_ips:
    variables[target_ip] = {
        'person_attr': None
    }

for target_ip in target_ips:
    if target_ip == 'ubuntu.hwanmoo.kr:8080':
        variables[target_ip]['cam_id'] = 1
        variables[target_ip]['detector'] = Detector(variables[target_ip]['cam_id'])

while True:
    for target_ip in target_ips:
        stage, gamedata = get_crest_data(target_ip)
        _v = variables[target_ip]
        if stage == 1:
            '''
            로비에서 대기중인 상황.
            crop_detector로 모니터링하다가 사람이 탑승하면 age/gender/color 파악하고 정보 저장.
            파악이 끝나면 기본 안내멘트 재생.
            재생 후 양손이 디텍트되면 게임 스타트 매크로 시작. + 스타트 멘트 재생
            '''
            d = _v['detector']
            print(_v['person_attr'])
            if _v['person_attr'] == None:
                person_attr = d.detect_start()
                print(":",person_attr)
                try:
                    if person_attr['gender'] != 'NA' and person_attr['gender'] != False:
                        _v['person_attr'] = person_attr
                        # d.detect_stop()
                except:
                    if person_attr[0]['gender'] != 'NA' and person_attr[0]['gender'] != False:
                        _v['person_attr'] = person_attr[0]
                        # d.detect_stop()
            else:
                # a_thread = Thread(target = playFile, args = (target_ip,'test_intro', ))
                # a_thread.start()

                print("Playing intro file, sleep for ", 27, "Seconds")
                
                # a_thread.join()

                pose_result = d.pose_start()

                if pose_result == 1:
                    a_thread = Thread(target = playFile, args = (target_ip,'test_gamestart', ))
                    a_thread.start()

                    a_thread.join()

                
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