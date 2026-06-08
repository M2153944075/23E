'''
实验名称：红色激光笔识别
实验平台：01Studio CanMV K230 + 3.5寸mipi屏
教程：wiki.01studio.cc
'''

import time, os, sys

from media.sensor import *
from media.display import *
from media.media import *

# 红色激光笔阈值 (L Min, L Max, A Min, A Max, B Min, B Max)
# 激光笔为高亮度红色，L值较高，可根据实际效果微调
laser_threshold = (67, 100, -19, 44, -14, 7)  # 推荐阈值

sensor = Sensor()
sensor.reset()
sensor.set_framesize(width=800, height=480)
sensor.set_pixformat(Sensor.RGB565)

Display.init(Display.ST7701, width=800, height=480, to_ide=True)
MediaManager.init()
sensor.run()

clock = time.clock()

while True:
    clock.tick()
    img = sensor.snapshot()

    # 寻找符合红色激光笔阈值的色块
    blobs = img.find_blobs([laser_threshold], pixels_threshold=10, area_threshold=10)

    if blobs:
        # 取面积最大的色块作为激光笔光斑（避免干扰）
        laser_blob = max(blobs, key=lambda b: b.area())
        # 在中心点绘制红色十字
        img.draw_cross(laser_blob.cx(), laser_blob.cy(),
                       color=(0, 0, 255), size=15, thickness=3)
        # （可选）在十字上方显示坐标
        img.draw_string_advanced(laser_blob.cx() + 10, laser_blob.cy() - 10, 20,
                                 "Laser", color=(0, 0, 255))

    # 显示FPS
    img.draw_string_advanced(0, 0, 30,
                             'FPS: ' + str("%.3f" % clock.fps()),
                             color=(255, 255, 255))
    Display.show_image(img)
    print(clock.fps())
