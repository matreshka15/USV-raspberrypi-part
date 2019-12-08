# 无人船上位机端程序
此为使用多线程开发的无人船上位机程序，即一个CPU即可处理多个任务。
## 功能
* 语音提示GPS连接情况、机体运行情况等。（只需要给上位机接一个小音箱）
* 使用遥控器控制
* 采集GPS坐标：此时在使用遥控器控制的同时，上位机在后台记录当前GPS坐标点
* 输入GPS坐标，自主导航。（输入坐标的方法可用Google Earth采点或使用之前采集的GPS坐标）
# 整体代码说明：
* LocationTrans文件夹内的脚本用于把从谷歌地球上采集的坐标点转换为GPS可用的坐标点。其中：
  * 谷歌地球中提取坐标点时会得到一个kml格式的文件，此时将其重命名为MapDataOutput.kml，拖进LocationTrans文件夹内
  * 点击kml2txt.py文件，此时会生成一个LatLong.txt文件，此即上位机可用的坐标文件（点开可以看到具体的GPS坐标）
  * txt2kml.py文件用于实现上述过程的反向实现。即：当你使用采点模式记录下载具走过的路线之后，载具上位机端会生成一个*.txt的坐标文件。点击txt2kml.py会将此文件转换为*.kml文件，打开*.kml即可直接在谷歌地球上观察载具之前记录的坐标点。
* sound文件夹用于存储语音提示时的音频
* AziFromPos.py将方位角转换为GPS坐标。即：输入目标点相对于载具的方位角（比如北偏东多少度），以及两点之间距离，此脚本会根据当前坐标点生成目标点的GPS坐标。
# 同时也在开发基于ROS的上位机程序
* [上位机端ROS版Github地址](https://github.com/matreshka15/ROS-based-unmanned-vehicle-project)  
建议使用非ROS版上位机程序，原因：开发环境容易配置（只需要Python），并且稳定性好。
* [姿态解算算法的解释与实机演示视频](https://zhuanlan.zhihu.com/p/82973264)
# 开发环境
在树莓派3B上开发，树莓派4上测试也没问题。理论支持任何支持python的开发板
# 其他
* 正在将此程序移植至ROS平台,连接：https://github.com/matreshka15/uas-raspi-ros
* 如有意向共同开发，请联系作者
* Email:8523429@qq.com
