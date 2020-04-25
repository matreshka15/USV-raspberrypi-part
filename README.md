# 无人船上位机端程序
此为使用多线程开发的无人船上位机程序，即一个CPU即可处理多个任务。
## 功能
* 语音提示GPS连接情况、机体运行情况等。（只需要给上位机接一个小音箱）
* 使用遥控器控制
* 采集GPS坐标：此时在使用遥控器控制的同时，上位机在后台记录当前GPS坐标点
* 输入GPS坐标，自主导航。（输入坐标的方法可用Google Earth采点或使用之前采集的GPS坐标）
# 使用说明
将整个工程文件用git clone的方式下载到某个目录下（比如桌面Desktop/UAS/），然后进入文件夹内，输入sudo python3 MainSequence.py即可。  
如有需要也可以直接将MainSequence.py配置为开机自启。
# 整体代码说明：
* LocationTrans文件夹内的脚本用于把从谷歌地球上采集的坐标点转换为GPS可用的坐标点。其中：
  * 谷歌地球中提取坐标点时会得到一个kml格式的文件，此时将其重命名为MapDataOutput.kml，拖进LocationTrans文件夹内
  * 点击kml2txt.py文件，此时会生成一个LatLong.txt文件，此即上位机可用的坐标文件（点开可以看到具体的GPS坐标）
  * txt2kml.py文件用于实现上述过程的反向实现。即：当你使用采点模式记录下载具走过的路线之后，载具上位机端会生成一个*.txt的坐标文件。点击txt2kml.py会将此文件转换为*.kml文件，打开*.kml即可直接在谷歌地球上观察载具之前记录的坐标点。
* sound文件夹用于存储语音提示时的音频
* AziFromPos.py将方位角转换为GPS坐标。即：输入目标点相对于载具的方位角（比如北偏东多少度），以及两点之间距离，此脚本会根据当前坐标点生成目标点的GPS坐标。
* Comm.py用于与下位机串口通信。
* Ctrl.py用于连接LoRa模块（没有也一样用，这里可以无视），同时获取坐标点用于导航。
* Record_Coordinates.py用于记录坐标点。
* Madgwick_AHRS_Test.py 用于评估算法收敛程度。在实际使用时可以无视这个文件。
* MainSequence.py 为主程序，负责上面提到的各个模块的调度与初始化等等。在使用时，需要显式调用的程序只有MainSequence.py。

# 同时也在开发基于ROS的上位机程序
* [上位机端ROS版Github地址](https://github.com/matreshka15/ROS-based-unmanned-vehicle-project)  
建议使用非ROS版上位机程序，原因：开发环境容易配置（只需要Python），并且稳定性好。
* [姿态解算算法的解释与实机演示视频](https://zhuanlan.zhihu.com/p/82973264)
### 重要！所有开发下位机过程中的开发日志以及手册均已存放在下面地址
* [开发无人船过程中参考的传感器手册以及算法资料](https://github.com/matreshka15/unmanned-ship-datasheets)
* 开发日志记录了项目从一开始的立项到后面一步步测试成功的大大小小细节。前后由于放弃了旧的姿态算法、选取了新的姿态算法，因此前期关于姿态的说明仅供参考用。
* 通信协议的部分已摘抄出来，放在超链接处的Repo目录下。即：整体框架与通信协议.docx

# 开发环境
在树莓派3B上开发，树莓派4上测试也没问题。理论支持任何支持python的开发板
# 其他
* 正在将此程序移植至ROS平台,连接：https://github.com/matreshka15/uas-raspi-ros
* 如有意向共同开发，请联系作者
* Email:8523429@qq.com
