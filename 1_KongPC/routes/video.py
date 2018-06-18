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

edit_video_blueprint = Blueprint('editVideo', __name__)
@edit_video_blueprint.route('/api/video', methods=['POST'])
def change_video_device():
    values = request.form
    print(values)
    if values == None:
        return 'Missing values', 400

    # Check that the required fields are in the POST'ed data
    required = ['devices']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Update video devices
    gv.video_target_devices = checkVideoDevices()

    updateVideoDevices(values["devices"])
    gv.video_target_devices = checkVideoDevices()

    results = {
        "total_devices": gv.total_video_devices,
        "active_devices": gv.video_target_devices
    }
    return jsonify(results), 201

get_video_blueprint = Blueprint('getVideo', __name__)
@get_video_blueprint.route('/api/video', methods=['GET'])
def get_video_device():
    gv.video_target_devices = checkVideoDevices()

    results = {
        "total_devices": gv.total_video_devices,
        "active_devices": gv.video_target_devices
    }
    return jsonify(results), 201

get_video_list_blueprint = Blueprint('getVideoList', __name__)
@get_video_list_blueprint.route('/api/videoList', methods=['GET'])
def get_video_list():
    gv.video_target_devices = checkVideoDevices()

    results = getVideoList()
    return jsonify(results), 201

stream_video_blueprint = Blueprint('streamVideo', __name__)
@get_video_list_blueprint.route('/api/streamVideo', methods=['POST'])
def stream_video():
    values = request.form

    if values == None:
        return 'Missing values', 400

    # Check that the required fields are in the POST'ed data
    required = ['dev']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Update video devices
    if gv.streaming == True:
        streaming_stop()
    else:
        streaming_start(values['dev'])

    results = {
        "total_devices": gv.total_video_devices,
        "active_devices": gv.video_target_devices,
        "status": gv.streaming
    }
    return jsonify(results), 201


