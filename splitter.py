from moviepy.editor import *
from skimage.measure import compare_ssim
import cv2
import threading
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import imageio_ffmpeg
import subprocess

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
        self.frame_points = [0, ]  # frame points after each cut
        self.time_points = [0, ]
        self.frames = []

    def get_audio(self):
        return self.audio_clip

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
        self.frame_points = [i for i in range(10)]
        for point_number in range(len(self.frame_points) - 1):
            sub = self.video_clip.subclip(0, 5)
            audio = self.audio_clip.subclip(0, 5)
            audio.write_audiofile('tempaudio.mp3')
            # a = AudioFileClip('tempaudio.mp3')
            # sub.set_audio(a)
            sub.write_videofile('lol.mp4')
            silent_video = r'C:\Users\79161\PycharmProjects\Video-splitter\loving.mp4'
            music = r'C:\Users\79161\PycharmProjects\Video-splitter\tempaudio.mp3'
            new = r'C:\Users\79161\PycharmProjects\Video-splitter\flower2.mp4'
            os.chdir(r'C:\Users\79161')
            # os.chdir(r'C:\Users\79161\ffmpeg\ffmpeg-20191215-ed9279a-win64-static\ffmpeg-20191215-ed9279a-win64-static\bin')
            os.system('dir')
            prog = subprocess.Popen(['runas', '/noprofile', '/user:Administrator', 'NeedsAdminPrivilege.exe'], stdin=subprocess.PIPE)
            prog.stdin.write('password'.encode())
            prog.communicate()
            subprocess.run(
                [r'C:\Users\79161\ffmpeg\ffmpeg-20191215-ed9279a-win64-static\ffmpeg-20191215-ed9279a-win64-static\bin', ' -i ', silent_video, ' -i ', music, ' -shortest', ' -c:v', ' copy', ' -c:a', ' aac', ' -b:a', ' 256k',
                 ' -y ', new])

            break

            # img_list = self.frames[self.frame_points[point_number]:(self.frame_points[point_number + 1]) - 1]
            # size = self.frames[0].shape
            # size = (size[1], size[0])
            # pics2vid(img_list=img_list, fps=self.fps, size=size,
            #          path_to_save=path_to_save, filename=f'{point_number}.mp4')
            # audio = self.audio_clip.subclip(self.frame_points[point_number], self.frame_points[point_number + 1])
            # pass

def pics2vid(img_list, fps, size, path_to_save, filename):
    # writer = imageio_ffmpeg.get_writer(path_to_save + '/' + filename, fps=fps)

    gen = imageio_ffmpeg.write_frames(os.path.join(path_to_save, filename), size=size, fps=fps)
    gen.send(None)  # seed the generator
    for img in img_list:
        gen.send(img)
    gen.close()
    # exit()
    # for img in img_list:
    #     pilimg = Image.fromarray(img)
    #     pilimg.save('img.jpg')
    #     writer.append_data(imageio.imread('img.jpg'))
    # writer.close()
    # size = img_list[0].shape
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # size = (size[0], size[1])
    # writer = cv2.VideoWriter(path_to_save, fourcc, fps, size)
    #
    # for i in range(len(img_list)):
    #     writer.write(np.array(img_list[i]))
    # writer.release()


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


def main(video_path):
    from time import time as t
    s = t()
    # run_splitter(num_threads=3, file_path=video_path)
    time_points, frame_points, frames = 0, 0, 0
    write_videos(time_points, frame_points, frames, file_path=video_path, path_to_save=r'utils/')
    print('TIME2:', t() - s)


main(video_path='11.mp4')
