from flask import Flask, request, jsonify, send_file
import os
from splitter import run_splitter, write_videos

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'mp4'}
path_to_save = '/'


def save_video(request):
    return ''


def zip_videos(videos_path):
    return 0


@app.route('/time_points', methods=['POST'])
def get_time_points():
    filename = save_video(request=request)
    time_points, frame_points, frames = run_splitter(num_threads=3, file_path=filename)
    return jsonify({'time_points': time_points})


@app.route('/frame_points', methods=['POST'])
def get_frame_points():
    filename = save_video(request=request)
    time_points, frame_points, frames = run_splitter(num_threads=3, file_path=filename)
    return jsonify({'frame_points': frame_points})


@app.route('/videos', methods=['POST'])
def get_frame_points():
    filename = save_video(request=request)
    time_points, frame_points, frames = run_splitter(num_threads=3, file_path=filename)
    write_videos(time_points, frame_points, frames, file_path=filename, path_to_save=r'utils/')
    video_zip = zip_videos(r'utils/')
    return send_file(video_zip, attachment_filename='capsule.zip', as_attachment=True)
