
import time, os, sys, gc
import cv_lite                 # cv_lite扩展模块 / cv_lite extension (C bindings)
import ulab.numpy as np        # MicroPython NumPy类库

from machine import Pin, Timer
from media.sensor import *     # 摄像头接口 / Camera interface
from media.display import *    # 显示接口 / Display interface
from media.media import *      # 媒体资源管理器 / Media manager
from machine import Pin
from machine import FPIOA
from machine import UART
#from Emm_V5 import EmmV5, SysParams



# ---------- 1. 视觉阈值与参数 ----------
# 红色激光笔阈值（LAB色彩空间）
laser_threshold = (91, 100, -22, 9, -9, 16)  # 推荐阈值

# 矩形检测参数（可根据实际图像调整）
canny_thresh1       = 48        # Canny 边缘检测低阈值 / Canny edge low threshold
canny_thresh2       = 155       # Canny 边缘检测高阈值 / Canny edge high threshold
approx_epsilon      = 0.04      # 多边形拟合精度（比例） / Polygon approximation precision (ratio)
area_min_ratio      = 0.001     # 最小面积比例（0~1） / Minimum area ratio (0~1)
max_angle_cos       = 0.5       # 最大角余弦（值越小越接近矩形） / Max cosine of angle (smaller closer to rectangle)
gaussian_blur_size  = 5         # 高斯模糊核大小（奇数） / Gaussian blur kernel size (odd number)
canny_thresh1       = 48        # Canny 边缘检测低阈值 / Canny edge low threshold
canny_thresh2       = 155       # Canny 边缘检测高阈值 / Canny edge high threshold
approx_epsilon      = 0.04      # 多边形拟合精度（比例） / Polygon approximation precision (ratio)
area_min_ratio      = 0.001     # 最小面积比例（0~1） / Minimum area ratio (0~1)
max_angle_cos       = 0.5       # 最大角余弦（值越小越接近矩形） / Max cosine of angle (smaller closer to rectangle)
gaussian_blur_size  = 5         # 高斯模糊核大小（奇数） / Gaussian blur kernel size (odd number)



# ---------- 2. 硬件初始化 ----------
fpioa = FPIOA()
# UART1初始化
fpioa.set_function(3,FPIOA.UART1_TXD)
fpioa.set_function(4,FPIOA.UART1_RXD)
uart1 = UART(UART.UART1, 115200) #设置串口号1和波特率
# UART2初始化
fpioa.set_function(11,FPIOA.UART2_TXD)
fpioa.set_function(12,FPIOA.UART2_RXD)
uart2 = UART(UART.UART2, 115200) #设置串口号1和波特率
# KEY初始化
fpioa.set_function(52,FPIOA.GPIO52)
fpioa.set_function(21,FPIOA.GPIO21)
LED=Pin(52,Pin.OUT) #构建LED对象,开始熄灭
KEY=Pin(21,Pin.IN,Pin.PULL_UP) #构建KEY对象
#state=0 #LED引脚状态
# 激光笔引脚初始化
fpioa.set_function(2,FPIOA.GPIO2)
jiguang=Pin(2,Pin.OUT)



# ---------- 3. 视觉初始化 ----------
# 图像尺寸设置 / Image resolution
image_shape = [480, 800]  # 高 x 宽 / Height x Width

# 初始化摄像头（灰度图模式） / Initialize camera (grayscale mode)
sensor = Sensor() #构建摄像头对象
sensor.reset() #复位和初始化摄像头

sensor.set_framesize(width=800, height=480, chn=0)   # 通道0：占位
sensor.set_pixformat(sensor.RGB565, chn=0)           # 随便给个格式

# 通道1：您的需求（800x480, RGB888）
sensor.set_framesize(width=800, height=480, chn=1)
sensor.set_pixformat(sensor.RGB888, chn=1)

# 通道2：您的需求（800x480, RGB565）
sensor.set_framesize(width=800, height=480, chn=2)
sensor.set_pixformat(sensor.RGB565, chn=2)

# 初始化显示器（IDE虚拟输出） / Initialize display (IDE virtual output)
Display.init(Display.ST7701, to_ide=True) #通过01Studio 3.5寸mipi显示屏显示图像
MediaManager.init()
# 初始化媒体系统 / Initialize media system
sensor.run()

# 启动帧率计时 / Start FPS timer
clock = time.clock()



# ---------- 矩形框识别 ----------
def detect_rectangle(img):

    gc.collect()

    img_np = img.to_numpy_ref()
    print("before")
    rects = cv_lite.rgb888_find_rectangles_with_corners(
            image_shape, img_np,
            canny_thresh1, canny_thresh2,
            approx_epsilon,
            area_min_ratio,
            max_angle_cos,
            gaussian_blur_size
        )
    if rects:
        best = max(rects, key=lambda r: r[2]*r[3])  # r[2]=w, r[3]=h
        # 提取四个角点：格式 (cx1,cy1, cx2,cy2, cx3,cy3, cx4,cy4) 索引4~11
        corners = [(best[4], best[5]), (best[6], best[7]),
                   (best[8], best[9]), (best[10], best[11])]
        return corners
    else:
        print("No rectangle detected.")
        return None

    gc.collect()

    img_np = img.to_numpy_ref()
    print("before")
    rects = cv_lite.rgb888_find_rectangles_with_corners(
            image_shape, img_np,
            canny_thresh1, canny_thresh2,
            approx_epsilon,
            area_min_ratio,
            max_angle_cos,
            gaussian_blur_size
        )
    if rects:
        best = max(rects, key=lambda r: r[2]*r[3])  # r[2]=w, r[3]=h
        # 提取四个角点：格式 (cx1,cy1, cx2,cy2, cx3,cy3, cx4,cy4) 索引4~11
        corners = [(best[4], best[5]), (best[6], best[7]),
                   (best[8], best[9]), (best[10], best[11])]
        return corners
    else:
        print("No rectangle detected.")
        return None



def sort_corners_clockwise(corners):
    """
    将四个角点排序为顺时针顺序（从左上角开始）
    corners: [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
    返回: [左上, 右上, 右下, 左下]
    """
    if corners is None or len(corners) != 4:
        print("Error: sort_corners_clockwise received invalid corners:", corners)
        return None
    if corners is None or len(corners) != 4:
        print("Error: sort_corners_clockwise received invalid corners:", corners)
        return None
    # 按 y 坐标排序，取前两个为顶部点，后两个为底部点
    sorted_by_y = sorted(corners, key=lambda p: p[1])
    top = sorted_by_y[:2]      # y 值较小的两个
    bottom = sorted_by_y[2:]   # y 值较大的两个
    # 在顶部点中，x 较小的为左上，x 较大的为右上
    top_left = min(top, key=lambda p: p[0])
    top_right = max(top, key=lambda p: p[0])
    # 在底部点中，x 较小的为左下，x 较大的为右下
    bottom_left = min(bottom, key=lambda p: p[0])
    bottom_right = max(bottom, key=lambda p: p[0])
    return [top_left, top_right, bottom_right, bottom_left]


def display_rectangles(img, corners):
    if corners is None or len(corners) != 4:
        return img
    img.draw_string_advanced(0,0,20,str(corners),color=(255,0,0))
    for i in range(4):
        img.draw_line(corners[i][0], corners[i][1], corners[(i+1)%4][0], corners[(i+1)%4][1], color=(0,255,0))
        img.draw_cross(corners[i][0], corners[i][1], color=(0,255,0), size=20, thickness=3)

    return img


def display_rectangles(img, corners):
    if corners is None or len(corners) != 4:
        return img
    img.draw_string_advanced(0,0,20,str(corners),color=(255,0,0))
    for i in range(4):
        img.draw_line(corners[i][0], corners[i][1], corners[(i+1)%4][0], corners[(i+1)%4][1], color=(0,255,0))
        img.draw_cross(corners[i][0], corners[i][1], color=(0,255,0), size=20, thickness=3)

    return img


 # ---------- 红色激光笔识别 ----------
def detect_RedBlobs(img):




    # 寻找符合红色激光笔阈值的色块
    blobs = img.find_blobs([laser_threshold], pixels_threshold=10, area_threshold=10)
    blobs = img.find_blobs([laser_threshold], pixels_threshold=10, area_threshold=10)

    if blobs:
        # 取面积最大的色块作为激光笔光斑（避免干扰）
        laser_blob = max(blobs, key=lambda b: b.area())
        # 在中心点绘制红色十字
        img.draw_cross(laser_blob.cx(), laser_blob.cy(),color=(0, 0, 255), size=15, thickness=3)
        # （可选）在十字上方显示坐标
        img.draw_string_advanced(laser_blob.cx() + 10, laser_blob.cy() - 10, 20,"Laser", color=(0, 0, 255))
        # （可选）在十字上方显示坐标
        img.draw_string_advanced(laser_blob.cx() + 10, laser_blob.cy() - 10, 20,"Laser", color=(0, 0, 255))
        return (laser_blob.cx(), laser_blob.cy())


    return None  # 未检测到则返回 None



 # ---------- 步进电机 ----------

# 按键变量
Key_Num = 0
CurrState = 0
PrevState = 0
case = 0

# 获取按键状态
def Key_GetNum():
    global Key_Num

    if Key_Num:
        temp = Key_Num
        Key_Num = 0
        return temp

    return 0



# 按键扫描任务
def Key_Tick(tim):

    global CurrState
    global PrevState
    global Key_Num

    PrevState = CurrState
    CurrState = 1 if KEY.value() == 0 else 0

    if CurrState == 0 and PrevState == 1:
        Key_Num = 1




## 启动定时器
#tim = Timer(-1)

#tim.init(
#    period=20,
#    mode=Timer.PERIODIC,
#    callback=Key_Tick
#)




 # ---------- 步进电机 ----------
#四角插值，平滑移动
#motor1 = EmmV5(uart1)
#motor2 = EmmV5(uart2)
#def lerp(p1,p2,n):

#    pts=[]

#    for i in range(n):

#        t=i/(n-1)

#        x=int(p1[0]+(p2[0]-p1[0])*t)
#        y=int(p1[1]+(p2[1]-p1[1])*t)

#        pts.append((x,y))

#    return pts








# ---------- 4. 状态机 ----------
# 状态定义
STATE_DETECT_RECT = 1    # 等待检测矩形
STATE_MOVE_TO_CORNER = 2 # 正在移向某个角点
STATE_DONE = 3           # 完成一圈

corners_clockwise = None  # 保存最近检测到的矩形角点

corners_clockwise = None  # 保存最近检测到的矩形角点

state = 0
red_pos = 0
count = 0
control_interval = 70
step = 0
count = 0
control_interval = 70
step = 0

# -------------------------------
# 主循环 / Main loop
# -------------------------------
while True:

    clock.tick()

    img = sensor.snapshot()
    img.draw_string_advanced(0, 0, 30,'FPS: ' + str("%.3f" % clock.fps()),color=(255, 255, 255))
    img.draw_string_advanced(0, 0, 30,'FPS: ' + str("%.3f" % clock.fps()),color=(255, 255, 255))

    red_pos = detect_RedBlobs(img)

    if state == STATE_DETECT_RECT:
        img_rgb888 = sensor.snapshot(chn = 1)
        corners = detect_rectangle(img_rgb888)
        corners_clockwise = sort_corners_clockwise(corners)
        print("Detected corners:", corners_clockwise)
        state = STATE_MOVE_TO_CORNER

    img = display_rectangles(img, corners_clockwise)
    count += 1
    print("count=", count)
    if count >= 100:
        state = STATE_DETECT_RECT
        count = 0

    Display.show_image(img)

    gc.collect()

    print("fps:", clock.fps())


# -------------------------------
# 程序退出与资源释放 / Cleanup on exit
# -------------------------------
sensor.stop()
Display.deinit()
os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
time.sleep_ms(100)
