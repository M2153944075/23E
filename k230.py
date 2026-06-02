import time, os, sys

from media.sensor import * #导入sensor模块，使用摄像头相关接口
from media.display import * #导入display模块，使用display相关接口
from media.media import * #导入media模块，使用meida相关接口
import time

sensor = None

try:
    print("camera_test")
    sensor = Sensor() #构建摄像头对象
    sensor.reset() #复位和初始化摄像头

    #sensor.set_framesize(Sensor.FHD) #设置帧大小FHD(1920x1080)，缓冲区和HDMI用,默认通道0
    sensor.set_framesize(width=800,height=480) #设置帧大小800x480,LCD专用,默认通道0
    sensor.set_pixformat(Sensor.RGB565) #设置输出图像格式，默认通道0


    #Display.init(Display.VIRT, sensor.width(), sensor.height(), to_ide=True) #通过IDE缓冲区显示图像
    Display.init(Display.ST7701, to_ide=True) #通过01Studio 3.5寸mipi显示屏显示图像
    #初始化媒体管理器
    MediaManager.init()
    #启动
    sensor.run()

    clock = time.clock()

    while True:
        clock.tick()
        os.exitpoint()
        img = sensor.snapshot (chn=CAM_CHN_ID_0)

        img_rect = img.to_grayscale(copy = True)
        img_rect = img_rect.binary([(67, 168)])
        rects = img_rect.find_rects(threshold=5000)
        for rect in rects:
            corner = rect.corners()
            img.draw_line(corner[0][0], corner[0][1], corner[1][0], corner[1][1], color=(0, 255, 0))
            img.draw_line(corner[1][0], corner[1][1], corner[2][0], corner[2][1], color=(0, 255, 0))
            img.draw_line(corner[2][0], corner[2][1], corner[3][0], corner[3][1], color=(0, 255, 0))
            img.draw_line(corner[3][0], corner[3][1], corner[0][0], corner[0][1], color=(0, 255, 0))

        img.draw_string_advanced(0,0,40,"fps:{}".format(clock.fps()),color=(255,0,0))
        Display.show_image(img)

        print("fps:{}".format(clock.fps()))

except KeyboardInterrupt as e:
    print("用户停止:",e)
except Exception as e:
    print(f"异常:{e}")
finally:
    if isinstance(sensor, Sensor):
        sensor.stop()
    Display.deinit()
    os.exitpoint(os.EXITPOINT_ENABLE_SLEEP)
    time.sleep_ms(100)
    MediaManager.deinit()
