from moviepy.editor import *
from skimage.measure import compare_ssim
import cv2
import threading


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
        current_time_point = self._start + self.frame_time
        while current_time_point < self._stop:
            current_frame = self.video_clip.get_frame(current_time_point)
            similarity = get_diff(previous_frame, current_frame, mode='color')
            if similarity < 0.30:
                self.time_points.append(round(current_time_point, accuracy))
                self.frame_points.append(round(current_time_point * self.fps))
            previous_frame = current_frame
            current_time_point += self.frame_time

    def get_frame_points(self):
        return self.frame_points

    def get_time_points(self):
        return self.time_points

    # def make_videos(self, path_to_save):
    #     print('Videos are being saved')
    #
    #     def write_video(finals, save_path, fps=self.fps):
    #         writer = imageio.get_writer(save_path, fps=fps)
    #         for final_img in finals:
    #             writer.append_data(final_img)
    #         writer.close()
    #
    #     for i in range(len(self.points) - 1):
    #         print('Writing')
    #         write_video(self.frames[self.points[i]:self.points[i + 1] - 1], path_to_save + '/' + str(i) + '.mp4',
    #                     self.fps)


def get_diff(im1, im2, mode='gray'):
    im1 = cv2.resize(im1, (200, 200))
    im2 = cv2.resize(im2, (200, 200))
    if mode == 'color':
        im1 = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
        im2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
    (score, diff) = compare_ssim(im1, im2, full=True)
    return score


class MyThread(threading.Thread):
    def __init__(self, number):
        threading.Thread.__init__(self)
        self.number = number
        self._return = None

    def run(self):
        video = Video(video_path='11.mp4')
        video.make_video_part(self.number, 3)
        video.find_points()
        message = "%s is running" % self.number
        print(message)
        self._return = video.get_time_points()

    def join(self, *args):
        threading.Thread.join(self)
        return self._return


def create_threads():
    threads = []
    for part in range(3):
        my_thread = MyThread(part)
        threads.append(my_thread)
        my_thread.start()
    for thread in threads:
        print(thread.join())


def old():
    from time import time as t
    s = t()
    video = Video(video_path='22.mp4')
    video.find_points()
    dt = t() - s
    print(f'SPEED: {(video._len * video.fps) / dt} files per second')
    print(f'SPEED: {video._len / dt} video seconds per second')
    print('TIME:', dt)
    print('frames:', video.get_frame_points())
    print('time points:', video.get_time_points())


def new():
    from time import time as t
    s = t()
    create_threads()
    print('TIME:', t() - s)


old()
# new()
