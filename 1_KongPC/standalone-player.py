from flask import Flask, jsonify, request, send_from_directory, make_response
from flask_cors import CORS

import json
from urllib.parse import urlparse

import atexit
import datetime
import time
import os

from pydub import AudioSegment
from pydub.playback import play
import pyaudio

from math import log, ceil, floor

dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)

def create_app():
    return app

app = create_app()  

@app.route('/status', methods=['GET'])
def status():
    return jsonify({}), 200

def make_chunks(audio_segment, chunk_length):
    """
    Breaks an AudioSegment into chunks that are <chunk_length> milliseconds
    long.
    if chunk_length is 50 then you'll get a list of 50 millisecond long audio
    segments back (except the last one, which can be shorter)
    """
    number_of_chunks = ceil(len(audio_segment) / float(chunk_length))
    return [audio_segment[i * chunk_length:(i + 1) * chunk_length]
            for i in range(int(number_of_chunks))]


@app.route('/play', methods=['GET'])
def play():
    req = request.args.get('path')

    file_path = dir
    for p in req.split('/'):
        if len(p) is not 0:
            file_path = os.path.join(file_path,p)

    seg = AudioSegment.from_wav(file_path)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt32,
                    channels=seg.channels,
                    rate=seg.frame_rate,
                    output=True)

    # break audio into half-second chunks (to allows keyboard interrupts)
    for chunk in make_chunks(seg, 500):
        stream.write(chunk._data)
    
    stream.stop_stream()
    stream.close()
    p.terminate()

    time.sleep(seg.duration_seconds)

    return jsonify({}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True, port=3000)