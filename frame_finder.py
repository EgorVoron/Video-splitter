from splitter import Video
import numpy as np
from PIL import Image

video = Video('11.mp4')
frame = Image.open('ssim/jpg/from_vif.PNG')
rgb_frame = frame.convert('RGB')
np_frame = np.array(rgb_frame)
print(video.find_frame(np_frame))
