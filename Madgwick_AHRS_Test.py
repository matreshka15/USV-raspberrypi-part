'''Copyright 2019 Eastar Tech 李东豫<8523429@qq.com>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.'''
'''
本脚本用于测试下位机由电子罗盘计算得到的偏航角与由姿态解算算法输出的偏航角的评估
使用前请确保下位机使用Eastar Protocol 发送偏航角数据
'''

#!/usr/bin/env python
# coding: utf-8
import matplotlib.pyplot as plt
import serial
import serial.tools.list_ports
import pylab as pl
import datetime
#船体姿态描述
class UASattitude:
    lattitude = 0
    longtitude = 0
    yaw = 0
    pitch = 0
    roll = 0
    speed = 0
    angleSpeed = 0
    dataProcessed = 0
    def __init__(self):
        self.latitude = 36.89198937216152
        self.longtitude = 120.5147411312813
        self.yaw = 11
        self.pitch = 12
        self.roll = 11
        self.dataProcessed = 0
        
ValidShip = UASattitude()
Ship = UASattitude()

################################################################
Port_online = 0
baudrate = 115200
port_list = list(serial.tools.list_ports.comports())

if(len(port_list)==0):
    print("无可用串口")
else:
    Port_online = 1
    print("当前以下端口在线：")
    for port in port_list:
        print(port)
    Port = input("请输入要打开的串口：")
    ser = serial.Serial(Port,baudrate)
    print("串口配置如下：:")
    print(ser,'\n')
    if ser.isOpen == False:
        ser.open()
    print("串口已启动")


beta = input("请输入当前滤波器增益:")
if(beta==''):
    beta = 'default'
timeSet = 10
timeSet = input("请输入数据采集的时间（以秒为单位）：")
if(timeSet.isdigit()):
    Start = 1
elif timeSet == '':
    timeSet = 10
    print("正在使用默认10s采集间隔进行")
else:
    Start = 0
    

if(Start):
    timeSequence1 = list()
    yawReceivedFromCompass = list()

    timeSequence2 = list()
    yawReceivedFromMadgwick = list()

    get0x73 = 0
    startBit = 0
    startTime = datetime.datetime.now()
    counter = 0
    counterForMagData = 0
    counterForMagCalibration = 0
    timeSpan = 0
    revData = list()
    dataIn = str()
    for cnt in range(22):#初始化列表
        revData.append(0)
    

    while True:

        #收到第一个数据时，开始记录采集时间
        if(not startBit):
            startTime = datetime.datetime.now()
            print("数据采集已开始。")
            
        #采集Madgwick输出姿态数据
        Ship.dataProcessed=0
        for cnt in range(22):#21为一帧数据的长度
            while(ser.inWaiting() ==0):
                pass
            if(not get0x73):
                revData[0] = ser.read(1)
            if(revData[0]==b's' or get0x73==1):
                get0x73 = 0
                revData[1] = ser.read(1)
                if(revData[1]==b'c'):
                    counter = 1
                    startBit = 1
                    #print("接受到引导码")
                    break
            elif (revData[0]==b'y'):
                revData[1] = ser.read(1)
                if(revData[1]==b'a'):
                    revData[2] = ser.read(1)
                    revData[3] = ser.read(1)
                    counterForMagData = 3
                    startBit =1
                    break
            else:
                counter = 0
                counterForMagData = 0

                
        #解析磁力计输出偏航角      
        if(counterForMagData==3):
            dataIn = str()
            getNumber = 0
            timeNow = datetime.datetime.now()
            getNumber = ser.read(1)
            while((getNumber.decode()).isdigit()):
                counterForMagData +=1  
                revData[counterForMagData] = getNumber
                getNumber = ser.read(1)
                if(counterForMagData>=4):
                    dataIn += revData[counterForMagData].decode()
                if(getNumber==b's'):
                    get0x73 = 1
                    revData[0] = 0X73
                else:
                    get0x73 = 0
            #print(dataIn)
            if(dataIn.isdigit()):
                yawReceivedFromCompass.append(eval(dataIn))
                timeSequence1.append((timeNow - startTime).seconds+((timeNow - startTime).microseconds)/1000000)
                ValidShip.dataProcessed=1
                counterForMagData = 0
                #print("磁罗盘姿态解算数据：yaw:%d"%(eval(dataIn)))
            else:
                counterForMagData = 0

        #解析Madgwick偏航角
        if(counter == 1):
            while(counter<21):#从1读到21 一共20个
                counter += 1
                revData[counter] = ord(ser.read(1))
            #print("读入数据集：",revData)
                    #验证环节：
            sumUp = 0
            timeNow = datetime.datetime.now()
            for temp in range(19):
                sumUp += revData[temp+2]
            sumUp = sumUp & 0xFF
                #print("Sum up is calculated to be %d"%self.sumUp)
            if sumUp == revData[21]:#校验和验证通过
                    #准备转化数据
                Ship.longtitude = bytes()
                Ship.lattitude = bytes()
                Ship.yaw = bytes()
                Ship.pitch = bytes()
                Ship.roll = bytes()
                    #开始转化数据
                for cnt in range(4):
                    Ship.longtitude += bytes([revData[cnt+2]])
                    Ship.lattitude += bytes([revData[cnt+2+4]])

                for cnt in range(2):
                        #print("%d八位数据：yaw:%d,pitch:%d,roll:%d"%(cnt,self.revData[cnt+10],self.revData[cnt+12],self.revData[cnt+14]))
                    Ship.yaw += bytes([revData[cnt+10]])
                    Ship.pitch += bytes([revData[cnt+12]])
                    Ship.roll += bytes([revData[cnt+14]])
                    #print(Ship.yaw)
                    
                ValidShip.yaw=int.from_bytes(Ship.yaw,byteorder='big',signed=False)
                ValidShip.pitch=int.from_bytes(Ship.pitch,byteorder='big',signed=True)
                ValidShip.roll=int.from_bytes(Ship.roll,byteorder='big',signed=True)
                ValidShip.lattitude = (int.from_bytes(Ship.lattitude,byteorder='big',signed=False)/1e7)
                ValidShip.longtitude = (int.from_bytes(Ship.longtitude,byteorder='big',signed=False)/1e7)
                    #数据转化完毕
                #print("MADGWICK姿态解算数据：yaw:%d,pitch:%d,roll:%d"%(ValidShip.yaw,ValidShip.pitch,ValidShip.roll))
                ValidShip.dataProcessed=1
                yawReceivedFromMadgwick.append(ValidShip.yaw)
                timeSequence2.append((timeNow - startTime).seconds+((timeNow - startTime).microseconds)/1000000)
                #print(revData)
            else:
                print("CRC校验失败")
                
        currentTime = datetime.datetime.now()
        last_timeSpan = timeSpan
        timeSpan = (currentTime - startTime).seconds
        if(last_timeSpan != timeSpan):
            print("当前数据采集时间:%dsec"%timeSpan)
        if(timeSpan>=eval(timeSet)):
            #计算误差
            errorTimeSequence = list()
            error = list()
            errorTimeSequence = timeSequence2
            if(len(timeSequence1)<= len(timeSequence2)):
                errorTimeSequence = timeSequence1
            print(len(timeSequence1),',',len(timeSequence2))
            for time in range(len(errorTimeSequence)):
                error.append(yawReceivedFromMadgwick[time]-yawReceivedFromCompass[time])
            #画图
            plot1 = pl.plot(timeSequence1,yawReceivedFromCompass,'b',label='Computed from Compass')
            plot2 = pl.plot(timeSequence2,yawReceivedFromMadgwick,'g',label='Computed from Algorithm')
            plot3 = pl.plot(errorTimeSequence,error,'r:',label='Error')
            pl.title(str("Madgwick Gradient Decent/Beta="+beta))
            pl.xlabel('Time Sequence/sec')
            pl.ylabel('Yaw/deg')
            pl.legend(loc='lower right')
            
            pl.savefig(str("C:\\Users\\85234\\Desktop\\Madgwick_Eval\\"+(datetime.datetime.now().strftime('%m%d-%H%M%S'))+'.png'),bbox_inches='tight')
            pl.show()
            request = input("是否继续？(y\\n)")
            if(request == 'y' or request == 'Y'):
                startBit = 0
                timeSet = input("请输入数据采集的时间（以秒为单位）：")
                print("程序继续运行中")
            else:
                break

