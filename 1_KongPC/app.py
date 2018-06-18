import sys
sys.path.insert(0, './routes')
sys.path.insert(0, './bin')
sys.path.insert(0, './config')

import globalVariables as gv

from flask import Flask, jsonify, request, send_from_directory, make_response
from flask_cors import CORS
from common import *
from video import *

import json
from urllib.parse import urlparse

from utils import *

import threading
import multiprocessing
import redis

import atexit
import datetime
import time
import os

gv.app_status = checkAppStatus()
gv.r = redis.StrictRedis(host='localhost', port=6379, db=0)

app = Flask(__name__)
CORS(app)

def create_app():
    serial_listener_start()
    atexit.register(interrupt)
    return app

app = create_app()  

# Add routes
app.register_blueprint(common_blueprint)
app.register_blueprint(edit_video_blueprint)
app.register_blueprint(get_video_blueprint)
app.register_blueprint(get_video_list_blueprint)

@app.route('/status', methods=['GET'])
def status():
    return jsonify(gv.app_status), 200

@app.route('/<path:path>', methods=['GET'])
def file_download(path):
    print(path)
    return send_from_directory('data/video', path, as_attachment=True)
    # file_name = 'data/video/' + path
    # response = make_response(app.send_static_file(file_name))
    # response.headers['content-length'] = str(os.path.getsize(file_name))
    # return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, port=3000)