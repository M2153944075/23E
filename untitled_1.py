import time, os, sys, gc
from machine import Pin
from machine import FPIOA
from machine import UART
from Emm_V5 import EmmV5, SysParams
from machine import Pin, Timer

fpioa = FPIOA()
# UART1初始化
fpioa.set_function(3,FPIOA.UART1_TXD)
fpioa.set_function(4,FPIOA.UART1_RXD)
uart1 = UART(UART.UART1, 115200) #设置串口号1和波特率
# UART2初始化
fpioa.set_function(11,FPIOA.UART2_TXD)
fpioa.set_function(12,FPIOA.UART2_RXD)
uart2 = UART(UART.UART2, 115200) #设置串口号1和波特率

motor1 = EmmV5(uart1)
motor2 = EmmV5(uart2)
# KEY初始化
fpioa.set_function(52,FPIOA.GPIO52)
fpioa.set_function(21,FPIOA.GPIO21)
LED=Pin(52,Pin.OUT) #构建LED对象,开始熄灭
KEY=Pin(21,Pin.IN,Pin.PULL_UP) #构建KEY对象
state=0 #LED引脚状态
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
motor1.origin_trigger_return(1,0,0)
motor2.origin_trigger_return(2,0,0)
print(0)
time.sleep(1)
motor2.pos_control(2, 0, 10, 5, 480, 0, 0)
print(1)

while True:
    if Key_GetNum():

        print(2)
        motor1.pos_control(1, 0, 10, 5, 470, 0, 0)


