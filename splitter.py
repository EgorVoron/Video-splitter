import threading
from time import time as t
from moviepy.editor import *
from skimage.measure import compare_ssim
import cv2


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
            if similarity < 0.45:
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
        for point_number in range(len(self.time_points) - 1):
            try:
                sub = self.video_clip.subclip(self.time_points[point_number], self.time_points[point_number + 1] - 1)
                audio = self.audio_clip.subclip(self.time_points[point_number], self.time_points[point_number + 1] - 1)
                audio.write_audiofile('tempaudio.mp3')
                a = AudioFileClip('tempaudio.mp3')
                sub.set_audio(a)
                sub.write_videofile(os.path.join(path_to_save, f'second{point_number}.mp4'))
            except Exception as exp:
                print(exp)
        print('Done')


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
        self._return = (video.get_time_points(), video.get_frame_points(), video.get_frames())

    def join(self, *args):
        threading.Thread.join(self)
        return self._return


def get_diff(im1, im2, mode='gray'):
    im1 = cv2.resize(im1, (200, 200))
    im2 = cv2.resize(im2, (200, 200))
    if mode == 'color':
        im1 = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
        im2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
    (score, diff) = compare_ssim(im1, im2, full=True)
    return score


def run_splitter(num_threads, file_path):
    threads = []
    for part in range(num_threads):
        split_thread = SplitThread(part, num_threads, file_path)
        threads.append(split_thread)
        split_thread.start()
    time_points, frame_points, frames = [], [], []
    for thread in threads:
        time_points += thread.join()[0]
        frame_points += thread.join()[1]
        frames += thread.join()[2]
    return time_points, frame_points, frames


def write_videos(time_points, frame_points, frames, file_path, path_to_save):
    full_video = Video(video_path=file_path)
    full_video.set_frame_points(frame_points)
    full_video.set_time_points(time_points)
    full_video.set_frames(frames)
    full_video.make_videos(path_to_save)


def main(video_path):
    s = t()
    time_points, frame_points, frames = run_splitter(num_threads=3, file_path=video_path)
    write_videos(time_points, frame_points, frames, file_path=video_path, path_to_save=r'utils/')
    print('TOTAL TIME:', t() - s)


main(video_path='11.mp4')
