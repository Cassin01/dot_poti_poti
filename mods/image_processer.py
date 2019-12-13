import numpy as np
import cv2
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.pyplot import *


# sideとupを求める関数
# sideはそのまま、upは転置して求める
def count(illust_map):
    num = []
    height, width = illust_map.shape[0:2]
    count = 0
    for i in range(height):
        countlist = []
        for j in range(width):
            if illust_map[i][j] == 0:
                if count != 0:
                    countlist.append(count)
                count = 0
            else:
                count += 1
        if len(countlist) == 0:
            countlist.append(0)
        num.append(countlist[::-1])
    return num

# def makeillust(img):
#     img_gray = cv2.cvtColor(img_resize, cv2.COLOR_BGR2GRAY)
#     kernel = np.ones((10,10),np.uint8)
#
#     gradient = cv2.morphologyEx(img_gray, cv2.MORPH_GRADIENT, kernel)
#     ret, illust_map = cv2.threshold(gradient, 127, 1, cv2.THRESH_BINARY) # 127を閾値として閾値処理
#     dilation = cv2.dilate(illust_map,kernel,iterations = 1) #膨張
#     img_re_d = cv2.resize(dilation,(50,50)) #膨張
#
#     return img_re_d

def makeillust_size(img, width, height):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((10,10),np.uint8)
    gradient = cv2.morphologyEx(img_gray, cv2.MORPH_GRADIENT, kernel)

    # ret, illust_map = cv2.threshold(img_gray, compute_mean(img_gray, width, height), 1, cv2.THRESH_BINARY) # 平均値を閾値として閾値処理(うまくいかない)
    ret, illust_map = cv2.threshold(gradient, 127, 1, cv2.THRESH_BINARY) # 127を閾値として閾値処理
    dilation = cv2.dilate(illust_map,kernel,iterations = 1) #膨張
    img_resize = cv2.resize(dilation, (width, height))
    return img_resize

# 平均値の計算
def compute_mean(img_gray, width, height):
    return sum(sum(img_gray) / (width * height))



# テスト用
if __name__ == '__main__':
    img = cv2.imread('../bird.jpg')
    # illust_map = makeillust(img)
    # side = count(illust_map)
    # up = count(illust_map.T)

    print(side)
    print(up)
