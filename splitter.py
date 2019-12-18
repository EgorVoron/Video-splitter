from moviepy.editor import *
from skimage.measure import compare_ssim
import cv2
import threading
# import matplotlib.pyplot as plt


class Video:
    def __init__(self, video_path):
        self.video_clip = VideoFileClip(video_path)
        self.fps = self.video_clip.fps
        self._len = self.video_clip.duration
        self._frame_number = self._len * self.fps
        self._start = 0
        self._stop = self._len
        self.frame_time = 1 / self.fps  # time per one frame
        self.frame_points = [0, ]  # frame points after each cut
        self.time_points = [0, ]
        self.frames = []

    def make_video_part(self, part, parts_num):
        self._len = self._len / parts_num
        self._frame_number = self._frame_number / parts_num
        self._start = self._len * part
        if part == 0:
            self._start = self.frame_time
        self._stop = self._len * (part + 1)

    def find_points(self, accuracy=9):
        previous_frame = self.video_clip.get_frame(self._start)
        self.frames.append(previous_frame)
        current_time_point = self._start + self.frame_time
        while current_time_point < self._stop:
            current_frame = self.video_clip.get_frame(current_time_point)
            similarity = get_diff(previous_frame, current_frame, mode='color')
            if similarity < 0.30:
                self.time_points.append(round(current_time_point, accuracy))
                self.frame_points.append(round(current_time_point * self.fps))
            self.frames.append(current_frame)
            previous_frame = current_frame
            current_time_point += self.frame_time

    def set_frame_points(self, frame_points):
        self.frame_points = frame_points

    def set_time_points(self, time_points):
        self.time_points = time_points

    def set_frames(self, frames):
        self.frames = frames

    def get_frames(self):
        return self.frames

    def get_frame_points(self):
        return self.frame_points

    def get_time_points(self):
        return self.time_points

    def make_videos(self, path_to_save):
        print('Writing...')
        for point_number in range(len(self.frame_points) - 1):
            writer = imageio.get_writer(path_to_save + '/' + str(point_number) + '.mp4', fps=self.fps)
            for img in self.frames[self.frame_points[point_number]:(self.frame_points[point_number + 1]) - 1]:
                writer.append_data(img)
            writer.close()


def get_diff(im1, im2, mode='gray'):
    im1 = cv2.resize(im1, (200, 200))
    im2 = cv2.resize(im2, (200, 200))
    if mode == 'color':
        im1 = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
        im2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
    (score, diff) = compare_ssim(im1, im2, full=True)
    return score


file_path = '11.mp4'


class SplitThread(threading.Thread):
    def __init__(self, number, num_threads):
        threading.Thread.__init__(self)
        self.number = number
        self.num_threads = num_threads
        self._return = None

    def run(self):
        video = Video(video_path=file_path)
        video.make_video_part(self.number, self.num_threads)
        video.find_points()
        self._return = (video.get_time_points(), video.get_frame_points(), video.get_frames())

    def join(self, *args):
        threading.Thread.join(self)
        return self._return


def run_splitter(num_threads):
    threads = []
    for part in range(num_threads):
        split_thread = SplitThread(part, num_threads)
        threads.append(split_thread)
        split_thread.start()
    time_points, frame_points, frames = [], [], []
    for thread in threads:
        time_points += thread.join()[0]
        frame_points += thread.join()[1]
        frames += thread.join()[2]
    return time_points, frame_points, frames


def write_videos(time_points, frame_points, frames, video_path, path_to_save):
    full_video = Video(video_path=video_path)
    full_video.set_frame_points(frame_points)
    full_video.set_time_points(time_points)
    full_video.set_frames(frames)
    full_video.make_videos(path_to_save)


# def old():
#     from time import time as t
#     s = t()
#     video = Video(video_path=SUKA)
#     video.find_points()
#     dt = t() - s
#     # print(f'SPEED: {(video._len * video.fps) / dt} files per second')
#     # print(f'SPEED: {video._len / dt} video seconds per second')
#     print('TIME1:', dt)
#     # print('frames:', video.get_frame_points())
#     # print('time points:', video.get_time_points())


def new():
    from time import time as t
    s = t()
    time_points, frame_points, frames = run_splitter(num_threads=3)
    write_videos(time_points, frame_points, frames, file_path, '/')
    print('TIME2:', t() - s)


new()
