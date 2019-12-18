import cv2
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
        countlist.append(count)
        num.append(countlist[::-1])
        count = 0
    return num

def makeillust_size(img, width, height):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((10,10),np.uint8)
    gradient = cv2.morphologyEx(img_gray, cv2.MORPH_GRADIENT, kernel)
    gradient = 255 - gradient

    # 127を閾値として閾値処理
    ret, illust_map = cv2.threshold(gradient, 127, 1, cv2.THRESH_BINARY)

    # 膨張
    dilation = cv2.dilate(illust_map,kernel,iterations = 1)
    img_resize = cv2.resize(dilation, (width, height))
    img_resize = 1 - img_resize
    return img_resize


# テスト用
if __name__ == '__main__':
    img = cv2.imread('../bird.jpg')
    illust_map = makeillust_size(img, 10, 10)
    side = count(illust_map)
    up = count(illust_map.T)

    print(side)
    print(up)
