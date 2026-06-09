# ============================================================
# MicroPython 灰度图矩形检测测试代码（使用 cv_lite 扩展模块）,带角点
# Grayscale Rectangle Detection Test using cv_lite extension
# ============================================================

import time, os, sys, gc
from machine import Pin, Timer
from media.sensor import *     # 摄像头接口 / Camera interface
from media.display import *    # 显示接口 / Display interface
from media.media import *      # 媒体资源管理器 / Media manager
import _thread
import cv_lite                 # cv_lite扩展模块 / cv_lite extension (C bindings)
import ulab.numpy as np        # MicroPython NumPy类库
from machine import Pin
from machine import FPIOA
from machine import UART
#from Emm_V5 import EmmV5, SysParams


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
state=0 #LED引脚状态
# 激光笔引脚初始化
fpioa.set_function(2,FPIOA.GPIO2)
jiguang=Pin(2,Pin.OUT)

# -------------------------------
# 图像尺寸设置 / Image resolution
# -------------------------------
image_shape = [480, 800]  # 高 x 宽 / Height x Width

# -------------------------------
# 初始化摄像头（灰度图模式） / Initialize camera (grayscale mode)
# -------------------------------

sensor = Sensor() #构建摄像头对象
sensor.reset() #复位和初始化摄像头

#sensor.set_framesize(Sensor.FHD) #设置帧大小FHD(1920x1080)，缓冲区和HDMI用,默认通道0
sensor.set_framesize(width=800,height=480) #设置帧大小800x480,LCD专用,默认通道0
sensor.set_pixformat(Sensor.RGB565) #设置输出图像格式，默认通道0

#sensor = Sensor(id=2, fps = 90)
#sensor.reset()

#sensor_width = sensor.width(None)
#sensor_height = sensor.height(None)
#sensor.set_framesize(width=image_shape[1], height=image_shape[0])
#sensor.set_pixformat(Sensor.RGB565)  # 灰度图格式 / Grayscale format

# -------------------------------
# 初始化显示器（IDE虚拟输出） / Initialize display (IDE virtual output)
# -------------------------------
Display.init(Display.ST7701, to_ide=True) #通过01Studio 3.5寸mipi显示屏显示图像

# -------------------------------
# 初始化媒体系统 / Initialize media system
# -------------------------------

sensor.run()

# -------------------------------
# 可选增益设置（亮度/对比度调节）/ Optional sensor gain setting
# -------------------------------

gain = k_sensor_gain()
gain.gain[0] = 20
sensor.again(gain)

# -------------------------------
# 启动帧率计时 / Start FPS timer
# -------------------------------
clock = time.clock()

# -------------------------------
# 矩形检测可调参数 / Adjustable rectangle detection parameters
# -------------------------------
canny_thresh1      = 50        # Canny 边缘检测低阈值 / Canny low threshold
canny_thresh2      = 150       # Canny 边缘检测高阈值 / Canny high threshold
approx_epsilon     = 0.04      # 多边形拟合精度比例（越小拟合越精确）/ Polygon approximation accuracy
area_min_ratio     = 0.001     # 最小面积比例（相对于图像总面积）/ Min area ratio
max_angle_cos      = 0.3       # 最大角度余弦（越小越接近矩形）/ Max cosine of angle between edges
gaussian_blur_size = 5         # 高斯模糊核尺寸（奇数）/ Gaussian blur kernel size

# =========================
# 按键变量
# =========================

Key_Num = 0
CurrState = 0
PrevState = 0
case = 0

# =========================
# 获取按键状态
# =========================

def Key_GetNum():
    global Key_Num

    if Key_Num:
        temp = Key_Num
        Key_Num = 0
        return temp

    return 0


# =========================
# 按键扫描任务
# 每20ms执行一次
# =========================

def Key_Tick(tim):

    global CurrState
    global PrevState
    global Key_Num

    PrevState = CurrState
    CurrState = 1 if KEY.value() == 0 else 0

    if CurrState == 0 and PrevState == 1:
        Key_Num = 1



# =========================
# 启动定时器
# =========================

tim = Timer(-1)

tim.init(
    period=20,
    mode=Timer.PERIODIC,
    callback=Key_Tick
)


#motor1 = EmmV5(uart1)
#motor2 = EmmV5(uart2)

count = 0
control_interval = 70
step = 0                # 0：空闲；1：等待执行第二步

# -------------------------------
# 主循环 / Main loop
# -------------------------------
while True:
    clock.tick()

    # 拍摄一帧图像 / Capture a frame

    img = sensor.snapshot()
    img_rect = img.to_grayscale(copy = True)

    img_np = img_rect.to_numpy_ref()


    # 调用底层矩形检测函数
    # 返回格式：[[x0, y0, w0, h0, c1.x, c1.y, c2.x, c2.y, c3.x, c3.y, c4,x, c4.y], [x1, y1, w1, h1,c1.x, c1.y, c2.x, c2.y, c3.x, c3.y, c4,x, c4.y], ...]
    rects = cv_lite.grayscale_find_rectangles_with_corners(
        image_shape, img_np,
        canny_thresh1, canny_thresh2,
        approx_epsilon,
        area_min_ratio,
        max_angle_cos,
        gaussian_blur_size
    )
    # 遍历检测到的矩形并绘制矩形框和角点
    for i in range(len(rects)):
        r = rects[i]
        corners = [(r[4],r[5]), (r[6],r[7]), (r[8],r[9]), (r[10],r[11])]
        img.draw_string_advanced(0,0,20,str(corners),color=(255,0,0))
        for j in range(4):
            img.draw_line(corners[j][0], corners[j][1], corners[(j+1)%4][0], corners[(j+1)%4][1], color=(0,255,0))
            img.draw_cross(corners[j][0], corners[j][1], color=(0,255,0), size=10, thickness=2)

##    count += 1
##    print(count)
##    if Key_GetNum():
##        case += 1
##        if case == 1:
##            jiguang.on()
##            LED.on()
##        elif case == 2:

##            LED.off()
##            # motor1 o_dir 0 左 1 右
##            # motor1 o_dir 0 下 1 上
##            #左下
##            motor1.pos_control(1, 0, 10, 5, 470, 0, 0)
##            motor2.pos_control(2, 0, 10, 5, 480, 0, 0)

##            start_count1 = count   # 记录当前帧计数（或直接 reset 一个专用计数器）
##            step = 1              # 进入等待第二步的状态

###            motor1.pos_control(1, 1, 100, 50, 300, 0, 0)
###            motor2.pos_control(2, 0, 100, 50, 197, 0, 0)

##            motor1.pos_control(1, 1, 100, 50, 300, 0, 0)
##            motor2.pos_control(2, 0, 100, 50, 197, 0, 0)
#        elif case == 3:
#            motor1.origin_trigger_return(1,0,0)
#            motor2.origin_trigger_return(2,0,0)
#            step = 0
#        else:
#            pass

#    # 状态处理：检查是否到了执行第二步的时机
#    #左上
#    if step == 1:
#        if (count - start_count1) >= control_interval:
#            # 间隔帧数已到，执行第二步
#            motor2.pos_control(2, 1, 10, 5, 960, 0, 0)
#            start_count2 = count   # 记录当前帧计数（或直接 reset 一个专用计数器）
#            step = 2              # 进入等待第二步的状态
#    #右上
#    elif step == 2:
#        if (count - start_count2) >= control_interval:
#            # 间隔帧数已到，执行第二步
#            motor1.pos_control(1, 1, 10, 5, 940, 0, 0)
#            start_count3 = count   # 记录当前帧计数（或直接 reset 一个专用计数器）
#            step = 3              # 进入等待第二步的状态
#    #右下
#    elif step == 3:
#        if (count - start_count3) >= control_interval:
#            # 间隔帧数已到，执行第二步
#            motor2.pos_control(2, 0, 10, 5, 960, 0, 0)
#            start_count4 = count   # 记录当前帧计数（或直接 reset 一个专用计数器）
#            step = 4              # 进入等待第二步的状态
#    #左下
#    elif step == 4:
#        if (count - start_count4) >= control_interval:
#            # 间隔帧数已到，执行第二步
#            motor1.pos_control(1, 0, 10, 5, 940, 0, 0)
#            count = 0   # 记录当前帧计数（或直接 reset 一个专用计数器）
#            step = 0              # 进入等待第二步的状态
#    else:
#        pass


    # 显示图像 / Show image
    img.draw_string_advanced(0,0,40,"fps:{}".format(clock.fps()),color=(255,0,0))

    Display.show_image(img)

    # 垃圾回收 & 输出帧率/ Garbage collect and print FPS
    gc.collect()
    print("fps:", clock.fps())

# -------------------------------
# 程序退出与资源释放 / Cleanup on exit
# -------------------------------
sensor.stop()
Display.deinit()
os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
time.sleep_ms(100)

