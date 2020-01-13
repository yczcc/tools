#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs,os,sys,shutil,re
import numpy as np
import time
from PIL import Image

Image.MAX_IMAGE_PIXELS = 100000000000

def imageRange(filePath):
    time_begin = time.time()

    img_src_file = Image.open(filePath)
    print "the picture's size: ", img_src_file.size

    img_src = np.array(img_src_file)

    v_max = img_src.shape[0]  # 竖向像素数，也就是最大x值
    h_max = img_src.shape[1]  # 横向像素数，也就是最大y值

    x_lt = 0  # 左上角点x坐标
    y_lt = 0  # 左上角点y坐标

    x_lb = v_max - 1  # 左下角点x坐标
    y_lb = 0  # 左下角点y坐标

    x_rt = 0  # 右上角点x坐标
    y_rt = h_max - 1  # 右上角点y坐标

    x_rb = v_max - 1  # 右下角点x坐标
    y_rb = h_max - 1  # 右下角点y坐标

    print(v_max, h_max)
    print "time cost: %f(s)" % (time.time() - time_begin)
    time_begin = time.time()

    r = 0
    g = 1
    b = 2
    r_query = 0
    g_query = 0
    b_query = 0

    result = np.where((img_src[:, :, r] == r_query) & (img_src[:, :, g] == g_query) & (img_src[:, :, b] == b_query))

    # 重构result数组

    print(result[0])
    print(result[1])
    print(result[0][0])
    print(result[1][0])
    print "time cost: %f(s)" % (time.time() - time_begin)
    time_begin = time.time()

    img_des = [255, 255, 255] - img_src
    img_des_file = Image.fromarray(img_des.astype("uint8"))
    img_des_file.save("result.png")
    
    print "time cost: %f(s)" % (time.time() - time_begin)

    # def removeAjcentPixFromResult(pix_coords):
    #    pix_lt.x = pix_coords.x - 1
    #    pix_lt.y = pix_coords.y - 1
    #    pix_t.x = pix_coords.x - 1
    #    pix_t.y = pix_coords.y
    #    pix rt.x = pix_coords.x - 1
    #    pix rt.y = pix_coords.y + 1
    #    pix_l.x = pix_coords.x
    #    pix_l.y = pix_coords.y - 1
    #    pix_r.x = pix_coords.x
    #    pix_r.y = pix_coords.y + 1
    #    pix_lb.x = pix_coords.x + 1
    #    pix_lb.y = pix_coords.y - 1
    #    pix_b.x = pix_coords.x + 1
    #    pix_b.y = pix_coords.y
    #    pix_rb.x = pix_coords.x + 1
    #    pix_rb.y = pix_coords.y + 1
    #
    #    remove(result[0][pix.x],result[1][pix.y]) from result
    # numpy.delete
    # numpy.unique

def findContours(filePath):
    time_begin = time.time()

    img_src_file = Image.open(filePath)
    print "the picture's size: ", img_src_file.size
    img_src_width = img_src_file.size[0]
    img_src_height = img_src_file.size[1]
    print "the picture's img_src_width: ", img_src_width, " img_src_height: ", img_src_height

    img_src_array = np.array(img_src_file)

    nodata_array = np.array([0, 0, 0])

    trace = []
    start_x = 0
    start_y = 0

    print("start Point (%d %d)" % (start_x, start_y))
    trace.append([start_x, start_y])

    # 8邻域 顺时针方向搜索
    neighbor = [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]]
    neighbor_len = len(neighbor)

    # 先从当前点的左上方开始，
    # 如果左上方也是黑点(边界点)：
    #         搜索方向逆时针旋转90 i-=2
    # 否则：
    #         搜索方向顺时针旋转45 i+=1
    i = 0
    cur_x = start_x + neighbor[i][0]
    cur_y = start_y + neighbor[i][1]

    is_contour_point = 0
    try:
        while not ((cur_x == start_x) and (cur_y == start_y)):
            is_contour_point = 0
            while is_contour_point == 0:
                if cur_x >= 0 & cur_y >= 0 & (img_src[cur_x][cur_y] == nodata_array).all():
                    is_contour_point = 1
                    trace.append([cur_x, cur_y])
                    i -= 2
                    if i < 0:
                        i += neighbor_len
                else:
                    i += 1
                    if i >= neighbor_len:
                        i -= neighbor_len
                cur_x = cur_x + neighbor[i][0]
                cur_y = cur_y + neighbor[i][1]
    except:
        print("throw error")

def findContours2(filePath):
    im = Image.open(filePath)  # 读取图片

    im_array = np.array(im)

    [m, n] = im_array.shape

    a = np.zeros((m, n))  # 建立等大小空矩阵
    a[0, 0] = 1  # 设立种子点

    nodata_array = np.array([0, 0, 0])

    k = 1  # 设立区域判断生长阈值

    flag = 1  # 设立是否判断的小红旗
    while flag == 1:
        flag = 0
        lim = (np.cumsum(im_array * a)[-1]) / (np.cumsum(a)[-1])
        for i in range(2, m):
            for j in range(2, n):
                if a[i, j] == 1:
                    for x in range(-1, 2):
                        for y in range(-1, 2):
                            if a[i + x, j + y] == 0:
                                if (abs(im_array[i + x, j + y] - lim) <= k):
                                    flag = 1
                                    a[i + x, j + y] = 1

    data = im_array * a  # 矩阵相乘获取生长图像的矩阵

def findContours3(filePath):
    time_begin = time.time()

    img_src_file = Image.open(filePath)
    print "the picture's size: ", img_src_file.size
    img_src_width = img_src_file.size[0]
    img_src_height = img_src_file.size[1]
    print "the picture's img_src_width: ", img_src_width, " img_src_height: " , img_src_height

    img_src_array = np.array(img_src_file)

    nodata_array = np.array([0,0,0])

    for i in range(0, img_src_width-1):
        for j in range(0, img_src_height-1):
            if (not (img_src_array[j][i] == nodata_array).all()) and (img_src_array[j+1][i] == nodata_array).all():
                img_src_array[j][i] = np.array([255,0,0])
                break

    for m in range(img_src_width-1, -1, -1):
        for n in range(img_src_height-1, -1, -1):
            if (img_src_array[n][m] == nodata_array).all() and (not (img_src_array[n-1][m] == nodata_array).all()):
                img_src_array[n][m] = np.array([255, 0, 0])
                break

    img_des_file = Image.fromarray(img_src_array.astype("uint8"))
    img_des_file.save("result.png")

    print "time cost: %f(s)" % (time.time() - time_begin)


def findContours4(filePath):
    time_begin = time.time()

    img_src_file = Image.open(filePath)
    print "the picture's size: ", img_src_file.size
    img_src_width = img_src_file.size[0]
    img_src_height = img_src_file.size[1]
    print "the picture's img_src_width: ", img_src_width, " img_src_height: ", img_src_height

    img_src_array = np.array(img_src_file)
    #print img_src_array

    # 左边
    #按列求前缀和
    img_src_array_cumsum = np.cumsum(img_src_array, 1)
    print "img_src_array_cumsum time cost: %f(s)" % (time.time() - time_begin)
    time_begin = time.time()
    #print img_src_array_cumsum

    # 无效数据全替换
    nodata_array = np.array([0, 0, 0])
    datamax_array = np.array([256, 256, 256])
    img_src_array_where = np.where(
        (img_src_array_cumsum[:, :, 0] ==0) & (img_src_array_cumsum[:, :, 1] ==0) & (img_src_array_cumsum[:, :, 2] ==0))
    print "img_src_array_where time cost: %f(s)" % (time.time() - time_begin)
    time_begin = time.time()
    for i in range(0, len(img_src_array_where[0])):
        img_src_array_cumsum[img_src_array_where[0][i]][img_src_array_where[1][i]] = datamax_array
    print "img_src_array_where replace time cost: %f(s)" % (time.time() - time_begin)
    time_begin = time.time()
    #print img_src_array_cumsum

    # 按列求最小值索引
    img_src_array_argmin = np.argmin(img_src_array_cumsum, 1)
    print "img_src_array_argmin time cost: %f(s)" % (time.time() - time_begin)
    time_begin = time.time()
    #print img_src_array_argmin

    # 右边
    img_src_array2 = np.fliplr(img_src_array)
    # 按列求前缀和
    img_src_array_cumsum2 = np.cumsum(img_src_array2, 1)
    print "img_src_array_cumsum2 time cost: %f(s)" % (time.time() - time_begin)
    time_begin = time.time()
    # print img_src_array_cumsum2

    # 无效数据全替换
    img_src_array_where2 = np.where(
        (img_src_array_cumsum2[:, :, 0] == 0) & (img_src_array_cumsum2[:, :, 1] == 0) & (
                    img_src_array_cumsum2[:, :, 2] == 0))
    print "img_src_array_where2 time cost: %f(s)" % (time.time() - time_begin)
    time_begin = time.time()
    for i in range(0, len(img_src_array_where2[0])):
        img_src_array_cumsum2[img_src_array_where2[0][i]][img_src_array_where2[1][i]] = datamax_array
    print "img_src_array_where2 replace time cost: %f(s)" % (time.time() - time_begin)
    time_begin = time.time()
    # print img_src_array_cumsum

    # 按列求最小值索引
    img_src_array_argmin2 = np.argmin(img_src_array_cumsum2, 1)
    img_src_array_argmin2 = img_src_width - img_src_array_argmin2
    print "img_src_array_argmin2 time cost: %f(s)" % (time.time() - time_begin)
    time_begin = time.time()
    # print img_src_array_argmin2

    for m in range(0, img_src_height):
        setbuf = img_src_array_argmin[m][0] - 50
        while (setbuf <= img_src_array_argmin[m][0]):
            if setbuf >=0 :
                img_src_array[m][setbuf] = np.array([255, 0, 0])
            setbuf += 1

    for m in range(0, img_src_height):
        setbuf = img_src_array_argmin2[m][0] + 50
        while (setbuf >= img_src_array_argmin2[m][0]):
            if setbuf < img_src_width :
                img_src_array[m][setbuf] = np.array([255, 0, 0])
            setbuf -= 1

    print "img_src_array_where contour time cost: %f(s)" % (time.time() - time_begin)
    time_begin = time.time()

    img_des_file = Image.fromarray(img_src_array.astype("uint8"))
    img_des_file.save("result.png")

    print "time cost: %f(s)" % (time.time() - time_begin)

if __name__ == '__main__':
    #findContours4("123.png")
    findContours4("test.png")
