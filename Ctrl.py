'''Copyright 2019 李东豫<8523429@qq.com>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.'''

#!/usr/bin/env python
# coding: utf-8
try:
    import AziFromPos
    import time
    import RPi.GPIO as GPIO
    import serial
except:
    print("Ctrl模块文件引入出错！")



def GPIOinit():
    #配置设备
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    try:
        GPIO.cleanup()
    except RuntimeWarning:
        pass

def GPIO_Shutoff():
    #关闭GPIO，清除配置
    GPIO.cleanup()
    print("GPIO已重置。")

    
#无线串口类
class WirelessUSART:
    MD0 = 0
    AUX = 0
    Status = 0
    def __init__(self):
        self.MD0 = 7
        self.AUX = 11
        GPIO.setup(self.MD0, GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(self.AUX, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    def EnterCfgMode(self):
        if(not GPIO.input(self.MD0)):
            GPIO.output(self.MD0, GPIO.HIGH)
            time.sleep(0.3)
        else:
            print("无线串口MD0处于置高状态，无法配置")
    def ExitCfgMode(self):
        if(GPIO.input(self.MD0)):
            GPIO.output(self.MD0, GPIO.LOW)
            time.sleep(0.5)
        else:
            print("无线串口未处于配置模式")
    def getAUXstatus(self):#读写都加上判断
        return GPIO.input(self.AUX)
    
#无线串口配置函数    
def ConfigWirelessPort(ser,wirelessPort):
    configureSuccess = 0
    string = str()
    wirelessPort.EnterCfgMode()
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    time.sleep(0.1)
    ser.write(b"AT\r\n")
    time.sleep(0.5)
    while ser.inWaiting() != 0:
        dataIn = ser.read()
        #dataIn = dataIn.decode()
        #print("data incoming:",dataIn)
        if(dataIn==b'O'):
            config = b"AT+RESET\r\n"
            ser.write(config)
            configureSuccess = 1
            time.sleep(0.2)
            print("无线串口已上线。")
            wirelessPort.Status = 1
            baudrate = 9600
            ser = serial.Serial("/dev/ttyAMA0",baudrate)
            break
    if(not configureSuccess):
        print("Wireless Serial Port Offline.")
        wirelessPort.Status = 0
        
    wirelessPort.ExitCfgMode()
    return ser
    



    
def AcquireMapData():
    try:        
        #读取所有点坐标
        f = open('LatLong.txt','r')
        Mapdata = {}
        for line in f:
            startIndex = line.find(':')
            endIndex = line.find(',')
            name = int(line[:startIndex])
            Position0 = float(line[startIndex+1:endIndex])
            startIndex = endIndex
            line = line[endIndex+1:]
            endIndex = line.find(',')
            Position1 = float(line[:endIndex])
            Mapdata[name] = [Position0,Position1]
        for key in Mapdata.keys():
            print("Point#%d:%s"%(key,str(Mapdata[key])))
        print("%d Points In Total."%len(Mapdata.keys()))
    except FileNotFoundError:
        print("Map Data Not Found!")
    f.close()
    return Mapdata

