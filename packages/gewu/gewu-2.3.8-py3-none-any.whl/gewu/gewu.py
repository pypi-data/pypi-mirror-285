'''
# 1.3.0
* 修改蓝牙的连接方式

# 1.2.5
* 优化串口模式STOP的时候停止码盘电机

# 1.2.4
* 修改串口的函数，防止混淆

# 1.2.3
* 优化蓝牙连接不显示的问题

# 1.2.1
* 增加CAR模式

# 1.2.0
* 优化蓝牙下的停止问题

# 1.1.8
* 修正电机的run函数

# 1.1.7
* 修正show_icon函数

# 1.1.6
* 修改sensor的错误拼写

# 1.1.5
* 增加set_angle_between

# 1.1.4
* Pin返回数字0/1取反

# 1.1.3
* 做了一些修复

# 1.1.2
* 优化MAC的串口兼容性
# 1.1.0
* 优化MAC下的串口和蓝牙连接
# 1.0.5
* 修正了PIN的BUG，增加电机的STOP接口

# 1.0.4
* 修改BUG,增加两个显示函数

# 1.0.3
* 增加motor中rotate的函数复用

# 1.0.2
* 修改接口，修改蓝牙的超时时间=5
# 1.0.1
* 增加IPC
# 1.0.0
* 删除配置文件相关逻辑
# 0.9.9
* 增加stop_gewu自动通过配置文件连接设备
# 0.9.8
* 修改没有连接发送stop问题
# 0.9.7
* 修正舵机控制等问题
# 0.9.6
* 增加扫描蓝牙的接口,扫描时间2秒。
# V0.9.5
* 修改中文注释
* 修改接口
# V0.9
* 优化蓝牙
# V0.8
* 优化颜色的接口，完善其他逻辑
* 优化蓝牙接口的稳定性
# V0.7
* 增加对中文的支持
# V0.6
* 增加BLE的支持。
* 将串口连接单独成一个函数接口
# V0.5
* 增加对码盘电机的支持
# V0.4
* 增加颜色传感器和超声波传感器的接口
# V0.3
* 增加lcd显示的icon接口等
# V0.2
* 修正了舵机部分错误
# V0.1
* 优化了舵机的接口
'''

import serial
import serial.tools.list_ports
from threading import Thread
import time
import asyncio
from bleak import BleakClient
from bleak import BleakScanner
import queue
import codecs
import sys
import websockets

STEP_WAIT_AA = 0
STEP_WAIT_BB = 1
STEP_WAIT_CMD = 2
STEP_WAIT_LEN = 3
STEP_WAIT_DATA = 4
STEP_WAIT_BCC = 5
STEP_WAIT_AA1 = 10
STEP_WAIT_AA2 = 11
STEP_WAIT_BB1 = 12
STEP_WAIT_BB2 = 13

HEADA=0xF0
HEADB=0x0C

uartRxstep = STEP_WAIT_AA
datacmd = 0
uartRxindex = 0
datalen = 0
UART_BUFF_SIZE = 255
uartdata = bytearray(UART_BUFF_SIZE)

btn_a_state = 1
btn_b_state = 1
mic_value = 0
pin_1_input = 0
pin_2_input = 0
light_value = 0
acc_x = 0
acc_y = 0
acc_z = 0

dist_result = bytearray(4) #存储4个端口的超声波数据
color_result = bytearray(16) #[result,r,g,b]
motor_result = [0] * 20 #[state,car,power,speed,count]
motor_result_flag = 0
car_status = 0

ble_connect_flag = 0
com_connect_flag = 0

ble_Client = 0
ble_queue = queue.Queue(512)

import socket
UDP_IP = "127.0.0.1"
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def _get_serialport():
    # 获取所有串口设备实例。
    # 如果没找到串口设备，则输出：“无串口设备。”
    # 如果找到串口设备，则依次输出每个设备对应的串口号和描述信息。
    ports_list = list(serial.tools.list_ports.comports())
    gewu_port = ""
    if len(ports_list) <= 0:
        print("无串口设备")
        return None
    else:
        #print("可用的串口设备如下：")
        for comport in ports_list:
            #print(list(comport)[0], list(comport)[1])
            if list(comport)[1].find('CH340') != -1:
                gewu_port = list(comport)[0]
            elif list(comport)[1].find('USB Serial') != -1:
                if list(comport)[0].find('wch') != -1:
                    gewu_port = list(comport)[0]
                    break
                gewu_port = list(comport)[0]
    if gewu_port !="":
        #print("Gewu Serial:" + gewu_port)
        return gewu_port
    else:
        return None

def _open_serial_port():
    gewu_port = _get_serialport()
    if gewu_port == None:
        print("搜索串口设备失败")
        print("请检查usb线是否已经连接上设备。")
        return None
    try:
        ser = serial.Serial(gewu_port, 115200)    # 打开COM17，将波特率配置为115200，其余参数使用默认值
    except Exception as e:
        #print('端口连接失败,错误原因：\n',e)
        print('USB连接失败!')
        print(gewu_port+'端口被占用!')
        return None
    if ser.isOpen():                        # 判断串口是否成功打开
        print("USB连接成功!")
        #write_config(ser.name)
        #print(ser.name)    # 输出串口号
    else:
        print("USB连接失败!")
        print("请检查usb线是否已经连接上设备。")
        return None
    ser.write(chr(0x03).encode("utf-8"))
    ser.write(chr(0x06).encode("utf-8")) #进入在线模式
    return ser

def getChecksum(cmd, data, len):
    checksum = 0
    checksum ^= cmd
    checksum ^= len
    for i in range (len):
        checksum ^= data[i]
    return checksum

def readCmd():
    global datacmd
    return datacmd

def readLen():
    global datalen
    return datalen

def readBytes(_len, index):
    global uartdata
    _data = []
    for i in range(_len):
        _data.append(uartdata[i+index])
    return _data

def recv_parse(_inByte):
    global uartRxstep, datacmd, uartRxindex, uartdata, datalen
    if uartRxstep == STEP_WAIT_AA:
        if _inByte == HEADA:
            uartRxstep = STEP_WAIT_BB
            #print("##A")
    elif uartRxstep == STEP_WAIT_BB:
        if _inByte == HEADB:
            uartRxstep = STEP_WAIT_CMD
        else:
            uartRxstep = STEP_WAIT_AA
    elif uartRxstep == STEP_WAIT_CMD:
        datacmd = _inByte
        uartRxstep = STEP_WAIT_LEN
    elif uartRxstep == STEP_WAIT_LEN:
        datalen = _inByte
        if datalen > 128: ##error
            uartRxstep = STEP_WAIT_AA
        uartRxindex = 0
        uartRxstep = STEP_WAIT_DATA
    elif uartRxstep == STEP_WAIT_DATA:
        uartdata[uartRxindex] = _inByte
        uartRxindex += 1
        if uartRxindex >= datalen:
            uartRxstep = STEP_WAIT_BCC
    elif uartRxstep == STEP_WAIT_BCC:
        uartRxstep = STEP_WAIT_AA
        if getChecksum(datacmd, uartdata, datalen) == _inByte:
            return True
        else:
            print('crc error')
    return False

def recv_data_handler(data):
    global btn_a_state,btn_b_state,mic_value,pin_2_input,light_value,acc_x,acc_y,acc_z,pin_1_input,dist_result,color_result,motor_result
    global motor_result_flag,car_status
    for ch in data:
        if recv_parse(ch) == True:
            cmd = readCmd()
            if cmd == 0x01: #广播数据
                [state] = readBytes(1, 0)
                [btn] = readBytes(1, 1)
                #print(btn)
                btn_b_state = btn & 0x01
                btn_a_state = (btn>>1) & 0x01
                #print("BTN "+str(btn_a_state)+" "+str(btn_b_state))
                [mic_value] = readBytes(1, 2)
                [pin_2_input] = readBytes(1, 3)
                [light_value] = readBytes(1, 4)
                [acc_1,acc_2,acc_3,acc_4,acc_5,acc_6] = readBytes(6, 5)
                acc_x = acc_1 |(acc_2<<8)
                acc_y = acc_3 |(acc_4<<8)
                acc_z = acc_5 |(acc_6<<8)
                [pin_1_input] = readBytes(1, 11)

            elif cmd == 0x0A: #超声波数据
                [p,d1,d2] = readBytes(3, 0)
                p = p - 0xE5
                dist_result[p] = (int)((d1 | (d2<<8))/10)
            elif cmd == 0x09: #颜色传感器
                    [p,a,b,c,d,e] = readBytes(6, 0)
                    p = p - 0xE5
                    color_result[4*p] = a
                    color_result[4*p+1] = b
                    color_result[4*p+2] = c
                    color_result[4*p+3] = d
            elif cmd == 0x08: #电机参数
                    [p] = readBytes(1, 0) #端口
                    p = p - 0xE9
                    [motor_state] = readBytes(1, 1)
                    [car_status] = readBytes(1, 2)
                    [deg1,deg2,deg3,deg4] = readBytes(4, 7)
                    deg = deg1 | (deg2<<8) |(deg3<<16)|(deg4<<24)
                    motor_result[5*p] = motor_state
                    if deg > 2147483647:
                        motor_result[5*p+4] = 4294967295 - deg
                    else:
                        motor_result[5*p+4] = deg
                    #print("deg "+ str(motor_result[5*p]) + " " + str(motor_result[5*p+4]))
                    motor_result_flag = 1

def recv_serial_handler(serial_port):
    global btn_a_state,btn_b_state,mic_value,pin_2_input,light_value,acc_x,acc_y,acc_z,pin_1_input,dist_result,color_result,motor_result
    global motor_result_flag
    try:
        while True:
            try:
                count = serial_port.inWaiting()
                if count > 0:
                    data = serial_port.read(count)
                    recv_data_handler(data)
                else:
                    time.sleep(0.001)
            except Exception as errorMsg:
                pass
    except KeyboardInterrupt:
        if port != None:
            port.close()

class Button():
    def is_pressed_A(self):
        if btn_a_state:
            return False
        else:
            return True

    def is_pressed_B(self):
        if btn_b_state:
            return False
        else:
            return True

def hex2str(n):
    if n >=0 and n<=9:
        return 0x30 + n
    else:
        return 0x41+ (n-0x0A)

async def my_coroutine():
    # 协程执行的代码
    print('134')
    await asyncio.sleep(3.0)

def pack_send_data(cmd, data, len):
    global port,ble_Client
    if ble_connect_flag == 0 and com_connect_flag == 0:
        return
    msg_send = bytearray(512)
    msg_send[0] = HEADA
    msg_send[1] = HEADB
    msg_send[2] = cmd
    msg_send[3] = len
    for i in range (len):
        msg_send[4 + i] = data[i]
    msg_send[4 + len] = getChecksum(cmd, data, len)
    if ble_connect_flag == 0:
        #_data = bytearray(128)
        for i in range (5 + len):
            try:
                port.write(chr(hex2str(msg_send[i]>>4)).encode("utf-8"))
                # print(chr(hex2str(msg_send[i]>>4)).encode("utf-8"))
                port.write(chr(hex2str(msg_send[i]&0x0f)).encode("utf-8"))
                # print(chr(hex2str(msg_send[i]&0x0f)).encode("utf-8"))
                #_data[2*i]=((hex2str(msg_send[i]>>4)).encode("utf-8"))
                #_data[2*i+1]=((hex2str(msg_send[i]&0x0f)).encode("utf-8"))
            except Exception as errorMsg:
                pass
        #port.write(_data)
    else:
        new_bytearray = msg_send[:(5 + len)]
        sock.sendto(new_bytearray, (UDP_IP, UDP_PORT))
        # for i in range (5 + len):
        #     ble_queue.put(hex2str(msg_send[i]>>4))
        #     ble_queue.put(hex2str(msg_send[i]&0x0f))

# def pack_send_data_ble(cmd, data, len):
#     global port,ble_Client
#     msg_send = bytearray(512)
#     msg_send[0] = HEADA
#     msg_send[1] = HEADB
#     msg_send[2] = cmd
#     msg_send[3] = len
#     for i in range (len):
#         msg_send[4 + i] = data[i]
#     msg_send[4 + len] = getChecksum(cmd, data, len)
#     for i in range (5 + len):
#         ble_queue.put(hex2str(msg_send[i]>>4))
#         ble_queue.put(hex2str(msg_send[i]&0x0f))

class OLED():
    def clear(self):
        _data = bytearray(2)
        _data[0] = 8
        _data[1] = 1
        pack_send_data(4, bytearray(_data), 2)

    def show(self):
        _data = bytearray(2)
        _data[0] = 9
        _data[1] = 1
        pack_send_data(4, bytearray(_data), 2)

    def set_text(self,x,y,font,data):
        _data = bytearray(512)
        _data[0] = 0
        _data[1] = x
        _data[2] = y
        pack_send_data(4, bytearray(_data), 3)

        _data[0] = 6
        # font_size = [6, 7, 11, 16]
        if font == 1:
            _data[1] = 0
        elif font == 2 :
            _data[1] = 1
        elif font == 3 :
            _data[1] = 2
        else:
            _data[1] = 3
        n = 2
        # for i in str(data):
        #     _data[n] = ord(i)
        #     n = n + 1
        for i in (str(data)).encode('gb2312'):
            # print(i)
            _data[n] = i
            n = n + 1
        pack_send_data(4, bytearray(_data), n)

    def show_text(self,x,y,font,data):
        self.clear()
        self.set_text(x,y,font,data)
        self.show()


    # pic = [OLED.LOGO_S, OLED.LOVE, OLED.STONE, OLED.SCISSORS, OLED.CLOTH, OLED.ANGERE, OLED.SMILE, OLED.CRY,OLED.SUN,OLED.SUN,OLED.MOON,OLED.EYE]
    def get_icon_index(self,name):
        if name == "logo":
            return 0
        elif name == "sun":
            return 9
        elif name == "moon":
            return 10
        elif name == "love":
            return 1
        elif name == "eye":
            return 11
        elif name == "happy":
            return 6
        elif name == "sad":
            return 7
        elif name == "angry":
            return 5
        elif name == "stone":
            return 2
        elif name == "yeah":
            return 3
        elif name == "palm":
            return 4
        elif name == "fist":
            return 0
        elif name == "left":
            return 0
        elif name == "up":
            return 0
        elif name == "down":
            return 0
        elif name == "right":
            return 0
        else:
            return 0

    def set_icon(self,x,y,n):
        _data = bytearray(4)
        _data[0] = 7
        _data[1] = x
        _data[2] = y
        _data[3] = self.get_icon_index(n)
        pack_send_data(4, bytearray(_data), 4)

    def show_icon(self,x,y,n):
        self.clear()
        self.set_icon(x,y,n)
        self.show()

    def draw_rect(self,x,y,l,w,type):
        _data = bytearray(6)
        if type == 0:#空心
            _data[0] = 2
        else:
            _data[0] = 3
        _data[1] = x
        _data[2] = y
        _data[3] = l
        _data[4] = w
        _data[5] = 1 #显示
        pack_send_data(4, bytearray(_data), 6)

    def clear_rect(self,x,y,l,w,type):
        _data = bytearray(6)
        if type == 0:#空心
            _data[0] = 2
        else:
            _data[0] = 3
        _data[1] = x
        _data[2] = y
        _data[3] = l
        _data[4] = w
        _data[5] = 0 #
        pack_send_data(4, bytearray(_data), 6)

    def draw_circle(self,x,y,r,type):
        _data = bytearray(5)
        if type == 0:#空心
            _data[0] = 4
        else:
            _data[0] = 5
        _data[1] = x
        _data[2] = y
        _data[3] = r
        _data[4] = 1 #显示
        pack_send_data(4, bytearray(_data), 5)
    def clear_circle(self,x,y,r,type):
        _data = bytearray(5)
        if type == 0:#空心
            _data[0] = 4
        else:
            _data[0] = 5
        _data[1] = x
        _data[2] = y
        _data[3] = r
        _data[4] = 0
        pack_send_data(4, bytearray(_data), 5)

class Servo():
    def __init__(self, r):
       self.port = r - 2

    def set_angle(self,angle):
        if angle > 180:
            angle = 180
        if angle < 0:
            angle = 0
        _data = bytearray(3)
        _data[0] = self.port
        a = 0
        # if angle == 90:
        #     a = 1500
        # elif angle == 0:
        #     a = 1000
        # elif angle == 180:
        #     a = 2000
        # else:
        a = (int)(angle*11)+400
        _data[1] = a & 0xff
        _data[2] = a >> 8
        pack_send_data(2, bytearray(_data), 3)

    def run(self,speed):
        if speed > 100:
            speed = 100
        if speed < -100:
            speed = -100
        if speed > 0 and speed < 25:
            speed = 25
        if speed < 0 and speed > -25:
            speed = -25

        _data = bytearray(3)
        _data[0] = self.port
        a = 5*speed +1500
        if a>2000:
            a = 2000
        _data[1] = a & 0xff
        _data[2] = a >> 8
        pack_send_data(2, bytearray(_data), 3)

    def stop(self):
        _data = bytearray(3)
        _data[0] = self.port
        a = 1500
        _data[1] = a & 0xff
        _data[2] = a >> 8
        pack_send_data(2, bytearray(_data), 3)
        #print('stop')
    def set_angle_between(self,start_angle,end_angle,secs=1):
        _data = bytearray(5)
        _data[0] = self.port
        _data[1] = start_angle
        _data[2] = end_angle
        s = secs * 1000
        _data[3] = s & 0xff
        _data[4] = s >> 8
        pack_send_data(0x0c, bytearray(_data), 5)
        time.sleep(1+secs)
# -100 1000
#  100 2000
#
class Pin():
    def __init__(self, r):
       self.port = r

    def get_digit(self):
        if self.port == 1:
            return  1 if pin_1_input > 100 else 0
        else:
            return 1 if pin_2_input > 100 else 0

    def get_analog(self):
        if self.port == 1:
            if pin_1_input < 20:
                return 0
            else:
                return pin_1_input
        else:
            if pin_2_input < 20:
                return 0
            else:
                return pin_2_input

class Audio():
    def play(self,name):
        _data = bytearray(3)
        _data[0] = 9
        _data[1] = self.get_sound_index(name)
        _data[2] = 1
        pack_send_data(1, bytearray(_data), 3)

    def get_sound_index(self,name):
        if name == "alert":
            return 1
        elif name == "car":
            return 2
        elif name == "door":
            return 3
        else:
            return 4

class Sensor():
    def __init__(self, r):
       self.port = r

    def get_distance(self):
        return dist_result[self.port - 5]

    def get_color(self):
        c = color_result[4*(self.port - 5)]
        #print(c)
        if c == 0:
            return "colorless"
        elif c == 1:
            return "red"
        elif c == 2:
            return "yellow"
        elif c == 3:
            return "green"
        elif c == 4:
            return "blue"
        elif c == 5:
            return "purple"
        elif c == 6:
            return "white"
        elif c == 7:
            return "black"
        else:
            return "colorless"

    def get_rgb(self):
        result = []
        result.append(color_result[4*(self.port - 5)+1])
        result.append(color_result[4*(self.port - 5)+2])
        result.append(color_result[4*(self.port - 5)+3])
        return result

class Motor():
    def __init__(self, r):
       self.port = 0xE0 + r

    def run(self,speed):
        if speed != 0:
            # _data = bytearray(4)
            # _data[0] = 0
            # _data[1] = self.port
            # _data[2] = speed&0xff
            # _data[3] = (speed >> 8)&0xff
            # pack_send_data(0x0A, bytearray(_data), 4) #设置速度

            # _data[0] = 4
            # _data[1] = self.port
            # _data[2] = 0x01
            # pack_send_data(0x0A, bytearray(_data), 3) #开始转动

            _data = bytearray(4)
            _data[0] = 0x0b
            _data[1] = self.port
            _data[2] = speed&0xff
            _data[3] = (speed >> 8)&0xff
            pack_send_data(0x0A, bytearray(_data), 4) #设置速度
        else:
            _data = bytearray(3)
            _data[0] = 1
            _data[1] = self.port
            _data[2] = 0x00
            pack_send_data(0x0A, bytearray(_data), 3) #STOP

    def stop(self):
        _data = bytearray(3)
        _data[0] = 1
        _data[1] = self.port
        _data[2] = 0x00
        pack_send_data(0x0A, bytearray(_data), 3) #STOP

    def _rotate(self,degree):
        global motor_result,motor_result_flag
        _data = bytearray(7)
        _data[0] = 0x0A
        _data[1] = self.port
        _data[2] = 1
        if degree < 0:
            _data[2] = 0
            degree = - degree
        _data[3] = (degree&0xff)
        _data[4] = (degree >> 8)&0xff
        _data[5] = (degree >> 16)&0xff
        _data[6] = (degree >> 24)&0xff
        pack_send_data(0x0A, bytearray(_data), 7)
        time.sleep(0.1)
        motor_result[5*(self.port -0xe0 - 9)] = 1
        while True:
            #print("### "+ str(motor_result[5*(self.port -0xe0 - 9)]))
            if motor_result[5*(self.port -0xe0 - 9)] == 0:
                break
            self.getMotorStatus()
            time.sleep(0.1)

    def rotate(self,degree,speed = 10):
        if speed != 0:
            _data = bytearray(4)
            _data[0] = 0
            _data[1] = self.port
            _data[2] = speed&0xff
            _data[3] = (speed >> 8)&0xff
            pack_send_data(0x0A, bytearray(_data), 4) #设置速度
            #转动
            self._rotate(degree)
        else:
            _data = bytearray(3)
            _data[0] = 1
            _data[1] = self.port
            _data[2] = 0x00
            pack_send_data(0x0A, bytearray(_data), 3) #STOP

    def set_zero(self):
        global motor_result,motor_result_flag
        _data = bytearray(3)
        _data[0] = 5
        _data[1] = self.port
        _data[2] = 0x00
        pack_send_data(0x0A, bytearray(_data), 3)
        motor_result[5*(self.port -0xe0 - 9)+4] = 0

    def getMotorStatus(self):
        _data = bytearray(3)
        _data[0] = 7
        _data[1] = self.port
        _data[2] = 0x00
        pack_send_data(0x0A, bytearray(_data), 3)

    def get_degree(self):
        global motor_result,motor_result_flag
        _data = bytearray(3)
        _data[0] = 8
        _data[1] = self.port
        _data[2] = 0x00
        pack_send_data(0x0A, bytearray(_data), 3)
        motor_result_flag = 0
        count = 0
        while True:
            if motor_result_flag == 1:
                break
            time.sleep(0.01)
            count = count + 1
            if count > 500:
                #print('error01 time out')
                break
        return motor_result[5*(self.port -0xe0 - 9)+4]

class CarMode:
    def set_state(self,state_str):
        _data = bytearray(3)
        _data[0] = 8
        state = 0
        if state_str == "top":
            state = 1
        elif state_str == "bottom":
            state = 2
        elif state_str == "left":
            state = 3
        elif state_str == "right":
            state = 4
        elif state_str == "front":
            state = 5
        elif state_str == "opposite":
            state = 6
        _data[1] = state
        pack_send_data(0x0B, bytearray(_data), 2)
        time.sleep(0.02)

    def set_port(self,left,right):
        _data = bytearray(3)
        _data[0] = 6
        _data[1] = 0xE0+left
        _data[2] = 0xE0+right
        pack_send_data(0x0B, bytearray(_data), 3)
        time.sleep(0.02)

    def run (self,speed):
        _data = bytearray(5)
        _data[0] = 0x0A
        _data[1] = speed&0xff
        _data[2] = (speed>>8)&0xff
        _data[3] = speed&0xff
        _data[4] = (speed>>8)&0xff
        pack_send_data(0x0B, bytearray(_data), 5)
        time.sleep(0.02)

    def stop(self):
        _data = bytearray(2)
        _data[0] = 4
        _data[1] = 0
        pack_send_data(0x0B, bytearray(_data), 2)
        time.sleep(0.02)

    def turn_left(self,degree):
        global car_status
        d=int(degree)*-1
        print(d)
        _data = bytearray(3)
        _data[0] = 2
        _data[1] = (d)&0xff
        _data[2] = ((d)>>8)&0xff
        print(_data[1])
        print(_data[2])
        pack_send_data(0x0B, bytearray(_data), 3)
        time.sleep(0.02)
        car_status = 1
        while True:
            #print("### "+ str(car_status))
            if car_status == 0:
                self.stop()
                break
            self.getMotorStatus()
            time.sleep(0.1)

    def turn_right(self,degree):
        global car_status
        d=int(degree)
        _data = bytearray(3)
        _data[0] = 2
        _data[1] = (d)&0xff
        _data[2] = ((d)>>8)&0xff
        pack_send_data(0x0B, bytearray(_data), 3)
        time.sleep(0.02)
        car_status = 1
        while True:
            #print("### "+ str(car_status))
            if car_status == 0:
                self.stop()
                break
            self.getMotorStatus()
            time.sleep(0.1)

    def getMotorStatus(self):
        # _data = bytearray(1)
        # _data[0] = 0x0E
        # pack_send_data(0x0B, bytearray(_data), 1)
        # time.sleep(0.1)
        _data = bytearray(3)
        _data[0] = 7
        _data[1] = 0xE9
        _data[2] = 0x00
        pack_send_data(0x0A, bytearray(_data), 3)
        time.sleep(0.1)

class Timer():
    def get_time(self):
        pass

car_mode = CarMode()

button = Button()
lcd = OLED()

p1 = Pin(1)
p2 = Pin(2)

class _ir_sensor:
    def __init__(self):
        self.P1 = Pin(1)
        self.P2 = Pin(2)

ir_sensor =_ir_sensor()

class _Servo180:
    def __init__(self):
        self.P3 = Servo(3)
        self.P4 = Servo(4)

class _Servo360:
    def __init__(self):
        self.P3 = Servo(3)
        self.P4 = Servo(4)

servo180 =_Servo180()
servo360 =_Servo360()

class _motor:
    def __init__(self):
        self.P9 = Motor(9)
        self.P10 = Motor(10)
        self.P11 = Motor(11)
        self.P12 = Motor(12)

motor = _motor()

class _color_sensor:
     def __init__(self):
        self.P5 = Sensor(5)
        self.P6 = Sensor(6)
        self.P7 = Sensor(7)
        self.P8 = Sensor(8)

color_sensor = _color_sensor()

class _distance_sensor:
     def __init__(self):
        self.P5 = Sensor(5)
        self.P6 = Sensor(6)
        self.P7 = Sensor(7)
        self.P8 = Sensor(8)

dis_sensor = _distance_sensor()

p5 = Sensor(5)
p6 = Sensor(6)
p7 = Sensor(7)
p8 = Sensor(8)

p9 = Motor(9)
p10 = Motor(10)
p11 = Motor(11)
p12 = Motor(12)

audio = Audio()

# print(hex2str(0x05))
# print(hex2str(0x0F))
port = 0
port_th = 0
def open_gewu_port():
    global port,ble_connect_flag,com_connect_flag,port_th
    port = _open_serial_port()
    if port == 0  or port == None:
        print("退出")
        quit()
    port_th = Thread(target=recv_serial_handler,args=(port,))
    port_th.start()
    ble_connect_flag = 0
    com_connect_flag = 1
    #t.join()

def read_config():
    f = open('config.txt', 'r')
    content = f.readline()
    #print('content: ' + content)
    f.close() # 当文件结束使用后记住需要关闭文件
    return content

def write_config(address):
    f = open('config.txt', 'w')
    f.writelines(address)
    f.close() # 当文件结束使用后记住需要关闭文件

'''
Date: 2024-01-11 19:16:55
author: zjs
description: 获取终端参数
'''
def getArg(val='---sokectPort'):
    for i, arg in enumerate(sys.argv):
        if(arg.startswith(val)):
            port = arg.split('=')
            return port[1]



def start_udp_server():
    global sock,ble_connect_flag
    sock.connect((UDP_IP, UDP_PORT))
    while True:
        socket_data, socket_addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        if socket_data[0] == 0xff:
            ble_connect_flag = 1
            print("GEWU 蓝牙连接成功")
        elif socket_data[0] == 0xfe:
            ble_connect_flag = 0
            print("GEWU 蓝牙连接失败")
        else:
        # print(f"Received message: {socket_data} from {socket_addr}")
            recv_data_handler(socket_data)

UDP_PORT = getArg('---blePort')
if UDP_PORT is not None:
    UDP_PORT = int(UDP_PORT)
    if UDP_PORT > 10000:
        ble_connect_flag = 1
    t2 = Thread(target=start_udp_server)
    t2.start()

def stop_gewu():#停止硬件运行，用于软件点击停止时调用
    global com_connect_flag,ble_connect_flag
    if ble_connect_flag == 0 and com_connect_flag == 0:
        #s = read_config()
        # if len(s) == 0:
        #     return
        # elif s.startswith('COM'):
        #     open_gewu_port()
        # else:
        #     open_gewu_ble(s)
        return
    _data = bytearray(1)
    _data[0] = 2
    pack_send_data(0x00, bytearray(_data), 1)
    time.sleep(0.1)
    if com_connect_flag == 1:
        port.write(chr(0x03).encode("utf-8"))
        port.write(chr(0x06).encode("utf-8")) #进入在线模式
        time.sleep(0.1)
        port.close()
        com_connect_flag = 0
        print('############################')
    if ble_connect_flag == 1:
        #ble_connect_flag = 0
        new_bytearray = bytearray([0x03, 0x06])
        sock.sendto(new_bytearray, (UDP_IP, UDP_PORT))
    time.sleep(1)

def ble(port):
    global ble_connect_flag,UDP_PORT
    ble_connect_flag = 1
    UDP_PORT = port
    # while True:
    #     sock.sendto(chr(0xff).encode('utf-8'), (UDP_IP, 5005))
    #     if ble_connect_flag == 1:
    #         break
    #     time.sleep(1)



'''
Date: 2024-01-11 19:17:50
author: zjs
description: 连接服务器
'''
async def runSokect():
    sokectPort = getArg()
    if sokectPort is None:
        print('socket端口不存在')
        return
    async with websockets.connect(f'ws://127.0.0.1:{sokectPort}') as websocket:
        try:
            while True:
                # 200ms接收数据
                recvMessage = await websocket.recv()
                recvMessage.startswith('stop_gewu')
                config = {
                    'jump': lambda:websocket.send('jump'.encode()),
                    'stop_gewu':lambda:(websocket.close(),stop_gewu())
                }
                activeMethod =  config[recvMessage]
                if activeMethod:
                    activeMethod()
                asyncio.sleep(0.2)

        except asyncio.IncompleteReadError:
            print("gewu sokect 客户端断了.")
        except Exception as e:
            print('gewu sokect 读写错误',e)


def open_gewu_ble_name():
    print('请联系老师更新gewu')

def runSokectWap():
    asyncio.run(runSokect())

sokectThread = Thread(target=runSokectWap)
sokectThread.start()


