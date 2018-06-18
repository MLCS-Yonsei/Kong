import sys
sys.path.insert(0, '../controllers')
sys.path.insert(0, '../')

sys.path.insert(0, '../config')
import globalVariables as gv

from index import controller

from flask import Flask, jsonify, request, Blueprint
import sqlite3
import json

from utils import *

common_blueprint = Blueprint('common', __name__)
@common_blueprint.route('/api/common', methods=['POST'])
def change_app_status():
    gv.app_status = checkAppStatus()

    values = request.form
    print(values)
    if values == None:
        return 'Missing values', 400

    # Check that the required fields are in the POST'ed data
    required = ['overtake', 'chase', 'mapDistance','ageGender','dataCollect','pcarsData','recording']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Update app status
    gv.app_status = update_status_with_form(values)
    run_process(gv.app_status)

    return jsonify(gv.app_status), 201

def run_process(app_status):
    # 종료 프로세스 일원화 -> 중첩 버그 발생 180531
    
    if app_status["deepLearning"]["ageGender"] == True:
        # Deep Learning Speaker
        dl_start()
    elif app_status["deepLearning"]["ageGender"] == False:
        dl_stop()

    if app_status["dataCollect"] == True:
        # Data Collector
        data_collect_start()

    elif app_status["dataCollect"] == False:
        data_collect_stop()

    if app_status["recording"] == True:
        # Record
        gv.video_target_devices = checkVideoDevices()
        record_start()
    elif app_status["recording"] == False:
        record_stop()

    if app_status["hooker"] == True:
        # Hooker
        gv.hooker = hooker_start()
    elif app_status["hooker"] == False:
        hooker_stop()

    if app_status["ruleBase"]["overtake"] == True or app_status["ruleBase"]["chase"] == True or app_status["ruleBase"]["mapDistance"] == True:
        # Rule Based Speaker
        rb_start()
    elif app_status["ruleBase"]["overtake"] == False and app_status["ruleBase"]["chase"] == False and app_status["ruleBase"]["mapDistance"] == False:
        rb_stop()

def update_status_with_form(values):
    for k in values:
        if k == "overtake":         gv.app_status["ruleBase"]["overtake"] = str2bool(values[k])
        if k == "chase":            gv.app_status["ruleBase"]["chase"] = str2bool(values[k])
        if k == "mapDistance":      gv.app_status["ruleBase"]["mapDistance"] = str2bool(values[k])
        if k == "ageGender":        gv.app_status["deepLearning"]["ageGender"] = str2bool(values[k])
        if k == "dataCollect":      gv.app_status["dataCollect"] = str2bool(values[k])
        if k == "pcarsData":        gv.app_status["pcarsData"] = str2bool(values[k])
        if k == "recording":        gv.app_status["recording"] = str2bool(values[k])
        if k == "serialActivate":   gv.app_status["serialActivate"] = str2bool(values[k])
        if k == "hooker":           gv.app_status["hooker"] = str2bool(values[k])

    updateAppStatus(gv.app_status)
    return gv.app_status
