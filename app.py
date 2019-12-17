from flask import Flask, request, jsonify, send_file
import os
from splitter import Splitter

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'mp4'}
path_to_save = '/'


def save_video(request):
    return ''


@app.route('/time_points', methods=['POST'])
def time_points():
    filename = save_video(request=request)
    splitter = Splitter(video_path=os.path.join(path_to_save, filename))
    splitter.find_points()
    return jsonify({'points': splitter.get_time_points()})


@app.route('/frame_points', methods=['POST'])
def frame_points():
    filename = save_video(request=request)
    splitter = Splitter(video_path=os.path.join(path_to_save, filename))
    splitter.find_points()
    return jsonify({'points': splitter.get_frame_points()})
