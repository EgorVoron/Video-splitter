from ssim.ssim_main import SSIM, Timer, saveData
import cv2
from imageio import imread


def get_diff(im1, im2, mode='color'):
    im1 = cv2.resize(im1, (200, 200))
    im2 = cv2.resize(im2, (200, 200))
    saveData('x_1920x1080.RGB', im1)
    saveData('y_1920x1080.RGB', im2)
    im1 = im1.astype('float32') / 255
    im2 = im2.astype('float32') / 255
    if mode == 'gray':
        im1 = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
        im2 = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
    score = SSIM(im1, im2, max_value=1)
    return score

if __name__ == "__main__":
    a = imread('ssim/jpg/0.jpg')
    b = imread('ssim/jpg/1.jpg')
    print(get_diff(a, b))



