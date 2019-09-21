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
import time
import Ctrl
import Comm
import serial
import threading
import AziFromPos
import Record_Coordinates
import os
systemOnline = 1#启动系统

#启动前配置：
Ctrl.GPIOinit()
baudrate = 921600
ser = serial.Serial("/dev/ttyAMA0",baudrate)
VEHECLE_LENGTH = 150 #载具的长度，单位为cm
print("Serial Port Configuration:")
print(ser)
if ser.isOpen == False:
    ser.open()

#状态机定义
STATE_NORMALLY_RUNNING=1
STATE_COLLECTING_POINTS=2
STATE_MANUAL_CTRL=3

#实例化各模块
Ship = Comm.UASattitude()
Route = Comm.Route()
ValidShip = Comm.UASattitude()
wirelessPort = Ctrl.WirelessUSART()
RingBuff = Comm.ringBuff(100,baudrate,wirelessPort,ser)
#创建多线程
tSynthesis = Comm.sysnthesisData(RingBuff,Ship,ValidShip,10,systemOnline)
tUART = Comm.USARTinData(RingBuff,systemOnline)
#创建线程池
THREADS = [tSynthesis,tUART]
try:
    for sub_thread in THREADS:
        sub_thread.start()
except:
    os.system('mplayer -really-quiet "/home/pi/RpiCentre/sound/subthreadserr.mp3"')

os.system('mplayer -really-quiet "/home/pi/RpiCentre/sound/SEQUENCESTART.mp3"')
time.sleep(0.5)

#启动主任务
try:
    startFromMinDistance = 0  #选择载具是从第一个点开始前进0还是就近开始前进1
    #读取路径轨迹
    while True:
        if(ValidShip.manual_automatic == STATE_NORMALLY_RUNNING):          
            if(ValidShip.fixtype == 0):
                os.system('mplayer -really-quiet "/home/pi/RpiCentre/sound/GPSNOFIX.mp3"')
            else:
                os.system('mplayer -really-quiet "/home/pi/RpiCentre/sound/GPSFIXED.mp3"')
            Mapdata = Ctrl.AcquireMapData()
            #上面是路线规划，下面是实时运行
            MaxDistance = VEHECLE_LENGTH #单位为cm
            #通过以上参数设定GPS点偏离的最大值，在GPS目标点的MaxDistance范围内视作已经经过了该点
            #自动选取路径起始点
            if(startFromMinDistance==0):
                nextPoint = min(Mapdata.keys())
            else:
                for key in Mapdata.keys():
                    distance = AziFromPos.distanceFromCoordinate(ValidShip.longtitude,ValidShip.lattitude,Mapdata[key][0],Mapdata[key][1])
                    if(key==1):
                        minimum = distance
                        indexMin = 1
                    else:
                        if(distance < minimum):
                            minimum = distance
                            indexMin = key
                nextPoint = indexMin
            print("Starting Point at #%d"%nextPoint)
            #===============参数设置=================           
            delay = 0.3
            freq = 1//delay
            delay_counter = 0
            #===============主程序运行===============
            while ValidShip.manual_automatic == STATE_NORMALLY_RUNNING:
                if ValidShip.dataProcessed==1:
                    time.sleep(delay)
                    if (Comm.Ship_Attitude_On_Screen(ValidShip)):
                        distance = AziFromPos.distanceFromCoordinate(ValidShip.longtitude,ValidShip.lattitude,Mapdata[nextPoint][0],Mapdata[nextPoint][1])
                        if distance >= 250:
                            distance = 250
                        angle =  AziFromPos.angleFromCoordinate(ValidShip.longtitude,ValidShip.lattitude,Mapdata[nextPoint][0],Mapdata[nextPoint][1])
                        Route.yaw = round(angle)
                        Route.distance = round(distance)
                        delay_counter += 1
                        if(delay_counter > 2*freq):
                            delay_counter = 0
                            print("Distance to next location：%.2fMeter"%(Route.distance/100))
                            print("Current Progress:%.2f%%"%(nextPoint/len(Mapdata.keys())*100))
                            print("%d Degrees to next location"%Route.yaw)
                        if(distance > MaxDistance):
                            #如果超出范围
                            pass 
                            #----根据夹角调转机头----#
                        elif(nextPoint == len(Mapdata.keys())):
                            #未超出范围，则已达到目标点。
                            nextPoint = nextPoint
                            Route.EndOfNav = 1
                            time.sleep(1)
                            os.system('mplayer -really-quiet "/home/pi/RpiCentre/sound/ARRIVEDEST.mp3"')
                        else:
                            Route.EndOfNav = 0
                            nextPoint += 1
                        Comm.SendNavMessege(ser,Route,wirelessPort)
        elif ValidShip.manual_automatic == STATE_COLLECTING_POINTS:
            if(Comm.Ship_Attitude_On_Screen(ValidShip)):
                index = 1
                Coordinates_Saving_File = open("LatLong_Record.txt","w+")
                print("Coordinate Saving File Created.")
                print("Recording Coordinates")
                while (ValidShip.manual_automatic==STATE_COLLECTING_POINTS):
                    time.sleep(0.7)#采点时间间隔设置
                    print('%ds Coordinates saved')
                    Record_Coordinates.start(Coordinates_Saving_File,index,ValidShip.longtitude,ValidShip.lattitude,0)
                    index += 1
                Coordinates_Saving_File.close()
                os.rename('LatLong_Record.txt','LatLong.txt')
                print("New Coordinates Saved")
        elif ValidShip.manual_automatic == STATE_MANUAL_CTRL:
            time.sleep(0.3)
            print('\fManually Controlling')
except KeyboardInterrupt:
    print('\f')
    systemOnline = 0
    tUART.stop()
    tSynthesis.stop()
    try:
        for sub_thread in THREADS:
            sub_thread.join()
        print("Sub-threads shutdown.")
    except RuntimeError:
        print("System Start Failure")
    try:
        if(not Coordinates_Saving_File.closed):
            Coordinates_Saving_File.close()
            print("Coordinates Saved.")
    except NameError:
        pass
    ser.flushInput()
    ser.close()
    print("Serial Port Closed")
    Ctrl.GPIO_Shutoff()
    os.system('mplayer -really-quiet "/home/pi/RpiCentre/sound/SYSTEMSHUTDOWN.mp3"')
    print("\n---System Offline---\n")
