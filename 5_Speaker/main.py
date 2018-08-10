# send_crest_request
from utils import *

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
            playFile(target_ip,'test_intro')
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