from moviepy.editor import *
from skimage.measure import compare_ssim
import cv2
import imageio


class Splitter:
    def __init__(self, video_path):
        self.video_clip = VideoFileClip(video_path)
        self.len = self.video_clip.duration
        self.fps = self.video_clip.fps
        self.frame_time = 1 / self.fps  # time per one frame
        self.frame_points = [0, ]  # frame points after each cut
        self.split_rate = 0.45
        self.time_points = [0, ]
        self.frames = []

    @staticmethod
    def get_diff(im1, im2, mode='gray'):
        im1 = cv2.resize(im1, (200, 200))
        im2 = cv2.resize(im2, (200, 200))
        if mode == 'color':
            im1 = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
            im2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
        (score, diff) = compare_ssim(im1, im2, full=True)
        return score

    def find_points(self, accuracy=9):
        previous_frame = self.video_clip.get_frame(self.frame_time)
        current_time_point = self.frame_time * 2
        while current_time_point < self.len:
            current_frame = self.video_clip.get_frame(current_time_point)
            similarity = self.get_diff(previous_frame, current_frame, mode='color')
            if similarity < self.split_rate:
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


# from time import time as t
#
# s = t()
# splitter = Splitter(video_path='11.mp4')
# splitter.find_points()
# print('frames:', splitter.get_frame_points())
# print('time points:', splitter.get_time_points())
# print('TIME:', t() - s)
