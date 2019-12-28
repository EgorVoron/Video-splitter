import threading
from time import time as t
from moviepy.editor import *
from skimage.measure import compare_ssim
import cv2
import os
import zipfile
import shutil


class Video:
    def __init__(self, video_path):
        self.video_clip = VideoFileClip(video_path)
        self.audio_clip = self.video_clip.audio
        self.fps = self.video_clip.fps
        self._len = self.video_clip.duration
        self._frame_number = self._len * self.fps
        self._start = 0
        self._stop = self._len
        self.frame_time = 1 / self.fps  # time per one frame
        self.frame_points = []  # frame points after each cut
        self.time_points = []
        self.frames = []

    def make_video_part(self, part, parts_num):
        self._len = self._len / parts_num
        self._frame_number = self._frame_number / parts_num
        self._start = self._len * part
        self._stop = self._len * (part + 1)

    def find_points(self, accuracy=5):
        previous_frame = self.video_clip.get_frame(self._start)
        self.frames.append(previous_frame)
        current_time_point = self._start + self.frame_time
        while current_time_point < self._stop:
            current_frame = self.video_clip.get_frame(current_time_point)
            similarity = self.get_ssim(previous_frame, current_frame)
            if similarity < 0.45:
                self.time_points.append(round(current_time_point, accuracy))
                self.frame_points.append(round(current_time_point * self.fps))
            self.frames.append(current_frame)
            previous_frame = current_frame
            current_time_point += self.frame_time

    def make_videos(self, path_to_save, thread_number):
        for point_number in range(len(self.time_points) - 1):
            try:
                sub = self.video_clip.subclip(self.time_points[point_number],
                                              self.time_points[point_number + 1] - self.frame_time)
                audio = self.audio_clip.subclip(self.time_points[point_number],
                                                self.time_points[point_number + 1] - self.frame_time)
                sub.set_audio(audio)
                sub.write_videofile(f'{path_to_save}/{thread_number}_{point_number}.mp4')
            except Exception as exp:
                print(exp)

    @staticmethod
    def get_ssim(im1, im2):
        im1 = cv2.resize(im1, (200, 200))
        im2 = cv2.resize(im2, (200, 200))
        im1 = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
        im2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
        (score, diff) = compare_ssim(im1, im2, full=True)
        return score


class SplitThread(threading.Thread):
    def __init__(self, number, num_threads, file_path):
        threading.Thread.__init__(self)
        self.number = number
        self.num_threads = num_threads
        self._return = None
        self.file_path = file_path

    def run(self):
        video = Video(video_path=self.file_path)
        video.make_video_part(self.number, self.num_threads)
        video.find_points()
        self._return = video

    def join(self, *args):
        threading.Thread.join(self)
        return self._return


def sum_points(videos):
    time_points_sum = []
    frame_points_sum = []
    for video in videos:
        time_points_sum += video.time_points
        frame_points_sum += video.frame_points
    return time_points_sum, frame_points_sum


def run_splitter(num_threads, file_path):
    threads = []
    for part in range(num_threads):
        split_thread = SplitThread(part, num_threads, file_path)
        split_thread.start()
        threads.append(split_thread)
    return [thread.join() for thread in threads]


def write_videos(path_to_save, videos):
    print('Writing...')
    # begin of don't touch
    for video_num, video in enumerate(videos[:-1]):
        video.time_points.append(videos[video_num + 1].time_points[0])
    videos[-1].time_points.append(videos[-1].video_clip.duration)
    # end of don't touch
    for n, video in enumerate(videos):
        video.make_videos(path_to_save, n)
    print('Writing finished')
    return


def zip_videos(videos_output_path, zip_output_path, zip_name):
    zipf = zipfile.ZipFile(os.path.join(zip_output_path, zip_name), 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(videos_output_path):
        for file in files:
            zipf.write(os.path.join(root, file))
    zipf.close()


def main(video_path):
    s = t()
    temp_videos_path = r'temp_videos_path/'
    if not os.path.exists(temp_videos_path):
        os.makedirs(temp_videos_path)
    videos = run_splitter(num_threads=3, file_path=video_path)
    time_points, frame_points = sum_points(videos)
    print('time points:', time_points)
    print('frame points:', frame_points)
    write_videos(path_to_save=temp_videos_path, videos=videos)
    zip_videos(videos_output_path=temp_videos_path, zip_output_path='', zip_name='videos.zip')
    shutil.rmtree(temp_videos_path)
    print('Done')
    print('TOTAL TIME:', t() - s)


main(video_path='11.mp4')
