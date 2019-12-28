from splitter import Video
from imageio import imread
import numpy as np

video = Video('11.mp4')
frame = imread('ssim/jpg/from_vif.PNG')
np_frame = np.array(frame)
print(video.find_frame(np_frame))
