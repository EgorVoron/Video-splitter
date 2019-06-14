import argparse
import moviepy
from moviepy.editor import *
from skimage.measure import compare_ssim
import cv2
import imageio
import numpy as np
from time import time

def get_diff(im1, im2, mode='gray'):
    im1 = cv2.resize(im1, (300, 300))
    im2 = cv2.resize(im2, (300, 300))
    if mode == 'color':
        im1 = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
        im2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
    (score, diff) = compare_ssim(im1, im2, full=True)
    diff = (diff * 255).astype("uint8")
    return score


class Splitter:
    def __init__(self, video_path):
        self.v = VideoFileClip(video_path)
        self.len = self.v.duration
        self.fps = self.v.fps
        self.frame_time = 1 / self.fps
        self.points = [0,] # кадры после монтажки
        self.frames = []
        
        
    def get_points(self):
        i = self.frame_time
        print('Start')
        while (i < self.len):
            getto = self.v.get_frame(i - self.frame_time)
            d = get_diff(getto, 
                         self.v.get_frame(i), mode='color')
            self.frames.append(getto)
            
            i += self.frame_time
            if d < 0.55: # 45 is better
                print(d)
                self.points.append(round(i * self.fps))
            
                
    def make_videos(self, path_to_save):         
        def write_video(finals, save_path, fps=self.fps):
            writer = imageio.get_writer(save_path, fps=fps)
            for final_img in finals:
                writer.append_data(final_img)
            writer.close()

        for i in range(len(self.points) - 1):
            print('Writing')
            write_video(self.frames[self.points[i]:self.points[i+1]-1], path_to_save + '/' + str(i) + '.mp4', self.fps)
                
    def make_videos(self, path_to_save):
        
        def write_video(finals, save_path, fps=self.fps):
            writer = imageio.get_writer(save_path, fps=fps)
            for final_img in finals:
                writer.append_data(final_img)
            writer.close()
            
        for i in range(len(self.points)):
            write_video(self.points[i:i+1], path_to_save + '/' + str(i), self.fps)
