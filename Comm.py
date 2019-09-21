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
# -*- coding: utf-8 -*

import serial
import time
import threading
import Ctrl
import os

#环形缓冲区类
class ringBuff:
    Head = 0
    Tail = 0
    data = []
    length = 0
    elements = 0
    def __init__(self,length,baud,WirelessPort,serial):
        self.length = length
        self.Head = 0
        self.Tail = 0
        self.elements = 0
        self.WirelessPort = WirelessPort
        self.ser = serial
        for cnt in range(length):#初始化列表
            self.data.append(0)
    def readData(self):
        if(self.elements >= self.length):
            return False
        else:
            dataIn = 'abc'
            if self.ser.inWaiting() != 0:
                if(self.WirelessPort.Status):
                    if(not self.WirelessPort.getAUXstatus()):
                        dataIn = self.ser.read(1) #读一个字节
                else:
                    dataIn = self.ser.read(1)
                #print("data in = %d"%ord(dataIn))
                if(dataIn != 'abc') :
                    if type(dataIn).__name__ == 'bytes':
                        dataIn = int.from_bytes(dataIn,byteorder='big',signed=False)
                    self.data[self.Tail] = dataIn
                    self.elements += 1
                    #print("正在读入，尾序号为%d,读入数据为%d"%(self.Tail,dataIn))
                    self.Tail = (1+self.Tail) % self.length

    def outputData(self):
        if(self.elements==0):
            return False
        else:  
            dataOut = self.data[self.Head]
            #print("正在输出，头序号为%d,输出数据为%d"%(self.Head,dataOut))
            self.elements -= 1
            self.Head = (self.Head+1) % self.length
            return dataOut
    def getLength(self):
        return self.elements
#船体姿态描述
class UASattitude:
    lattitude = 0
    longtitude = 0
    fixtype = 0
    hAcc = 0
    yaw = 0
    pitch = 0
    roll = 0
    speed = 0
    angleSpeed = 0
    dataProcessed = 0
    #手动、自动模式标志位，1表示自动;2表示采点;3表示手动
    manual_automatic = 1
    def __init__(self):
        self.lattitude = 0
        self.longtitude = 0
        self.yaw = 1
        self.pitch = 1
        self.roll = 1
        self.fixtype = 0
        self.dataProcessed = 0
        self.manual_automatic = 3
#路线规划描述：        
class Route:
        yaw = 0 #单位：°
        distance = 0#单位：厘米,u16型数据
        EndOfNav = 0#导航结束标志位
        def __init__(self):
            self.yaw = 0
            self.distance = 0
            self.EndOfNav = 0
def SendNavMessege(ser,Route,WirelessPort):
    sendFile = list()
    sumup = 0
    for cnt in range(20):
        sendFile.append(0) #初始化数组
    sendFile[0]=0x63
    sendFile[1]=0x73
    sendFile[2]=(Route.yaw&0xff00)>>8
    sendFile[3]=Route.yaw&0xff
    sendFile[4]=(Route.distance&0xff00)>>8
    sendFile[5]=Route.distance&0xff
    sendFile[6]=(Route.EndOfNav << 7)&0xff
    #这里用来后续填充
    for cnt in range(17):
        sumup+=sendFile[2+cnt]
    sumup = sumup & 0xff
    sendFile[19] = sumup
    sendBytes = bytes()
    for cnt in range(20):
        sendBytes += bytes([sendFile[cnt]])
    if(WirelessPort.Status):
        if(not WirelessPort.getAUXstatus()):
            ser.write(sendBytes)
    else:
        ser.write(sendBytes)
                        
#部署线程
class sysnthesisData(threading.Thread):
    revData = list()
    counter = 0
    delay = 0
    sumUp = 0
    def __init__(self,RingBuff,Ship,ValidShip,freq,systemFlag):
        threading.Thread.__init__(self)
        time.sleep(0.5)
        self.ObjRingBuff = RingBuff
        self.Ship = Ship
        self.ValidShip = ValidShip
        self.freq = freq
        self.delay = 1/freq
        self.systemFlag = systemFlag
        for cnt in range(22):#初始化列表
            self.revData.append(0)
        print("Eastar Protocol Data Frame Length Configuration：%d"%len(self.revData))
    def run(self):
        while self.systemFlag:
            time.sleep(self.delay)
            if(self.ObjRingBuff.getLength()>=22):
                for cnt in range(22):#21为一帧数据的长度
                    self.revData[0] = self.ObjRingBuff.outputData()
                    if(self.revData[0]==0x73):
                        self.revData[1] = self.ObjRingBuff.outputData()
                        if(self.revData[1]==0x63):
                            self.counter = 1
                            #print("接受到引导码")
                            break
                    else:
                        self.counter = 0

            if(self.counter == 1):
                while(self.counter<21):#从1读到21 一共20个
                    self.counter += 1
                    self.revData[self.counter] = self.ObjRingBuff.outputData()
                    #print("读入数据集：",self.revData)
                #验证环节：
                self.sumUp = 0
                for temp in range(19):
                    self.sumUp += self.revData[temp+2]
                self.sumUp = self.sumUp & 0xFF
                #print("Sum up is calculated to be %d"%self.sumUp)
                if self.sumUp == self.revData[21]:#校验和验证通过
                        #准备转化数据
                    threadLock.acquire()
                    self.Ship.longtitude = bytes()
                    self.Ship.lattitude = bytes()
                    self.Ship.yaw = bytes()
                    self.Ship.pitch = bytes()
                    self.Ship.roll = bytes()
                        #开始转化数据
                    for cnt in range(4):
                        self.Ship.longtitude += bytes([self.revData[cnt+2]])
                        self.Ship.lattitude += bytes([self.revData[cnt+2+4]])

                    for cnt in range(2):
                            #print("%d八位数据：yaw:%d,pitch:%d,roll:%d"%(cnt,self.revData[cnt+10],self.revData[cnt+12],self.revData[cnt+14]))
                        self.Ship.yaw += bytes([self.revData[cnt+10]])
                        self.Ship.pitch += bytes([self.revData[cnt+12]])
                        self.Ship.roll += bytes([self.revData[cnt+14]])
                    if(self.Ship.yaw!=b'00' and self.Ship.pitch!=b'00' and self.Ship.roll!=b'00'):
                        self.ValidShip.yaw=int.from_bytes(self.Ship.yaw,byteorder='big',signed=False)
                        self.ValidShip.pitch=int.from_bytes(self.Ship.pitch,byteorder='big',signed=True)
                        self.ValidShip.roll=int.from_bytes(self.Ship.roll,byteorder='big',signed=True)
                        #print(0xc0 & int.from_bytes(bytes([self.revData[20]]),byteorder='big',signed=False))
                        self.ValidShip.fixtype = (0xc0 & int.from_bytes(bytes([self.revData[20]]),byteorder='big',signed=False)) >> 6
                        self.ValidShip.manual_automatic = (0x30 & int.from_bytes(bytes([self.revData[20]]),byteorder='big',signed=False)) >> 4
                        self.ValidShip.hAcc = int.from_bytes(bytes([self.revData[16]]),byteorder='big',signed=False)
                        self.ValidShip.lattitude = (int.from_bytes(self.Ship.lattitude,byteorder='big',signed=False)/1e7)
                        self.ValidShip.longtitude = (int.from_bytes(self.Ship.longtitude,byteorder='big',signed=False)/1e7)
                        self.ValidShip.dataProcessed=1
                        #数据转化完毕
                    threadLock.release()
                    #print("%d八位数据：yaw:%d,pitch:%d,roll:%d"%(self.ValidShip.yaw,self.ValidShip.pitch,self.ValidShip.roll))
                    

                else:
                    print("CRC Failed to validate")
                    pass

    def stop(self):
        self.systemFlag = 0



class USARTinData(threading.Thread):
    def __init__(self,RingBuff,systemFlag):
        time.sleep(0.5)
        threading.Thread.__init__(self)
        self.RingBuff = RingBuff
        self.systemFlag = systemFlag
    def run(self):
        print("Serial port started")
        while self.systemFlag:
            self.RingBuff.readData()
    def stop(self):
        self.systemFlag = 0

class SendCommand(threading.Thread):
    def __init__(self,ser,ValidShip,Route,WirelessPort,freq,systemFlag):
        threading.Thread.__init__(self)
        time.sleep(1)
        self.serial = ser
        self.Route = Route
        self.ValidShip = ValidShip
        self.WirelessPort = WirelessPort
        self.freq = freq
        self.delay = 1/self.freq
        self.systemFlag = systemFlag 
    def run(self):
        while self.systemFlag:
            if (self.ValidShip.fixtype != 0):
                time.sleep(self.delay)
                #SendNavMessege(self.serial,self.Route,self.WirelessPort)
        
    def cease(self):
        self.systemFlag = 0
    def recover(self):
        self.systemFlag = 1


threadLock = threading.Lock()


def Ship_Attitude_On_Screen(ValidShip):
    fixtype = {0:"No fix",1:"Dead reckoning only",2:"2D-fix",3:"3D-fix",4:"GNSS + dead reckoning combined",5:"Other fixtype"}
    print("Yaw：%d\n"%(ValidShip.yaw))
    print(fixtype[ValidShip.fixtype])
    if(ValidShip.fixtype != 0):
        print("=>Longtitude：%.7f\n=>Latitude：%.7f"%(ValidShip.longtitude,ValidShip.lattitude))
        print("hAcc:%.1fMeter"%(ValidShip.hAcc/10))
        return 1
    return 0
