#!/usr/bin/env python
# coding: utf-8

# In[132]:
outputData={}
StartLoop = 0
nameNotFound = 1
posNotFound = 1


# In[133]:


f = open("MapData.kml","r",encoding='gb18030',errors='ignore')
fw = open("LatLong.txt","w")


# In[134]:
f.seek(0,0)  #首先把文件指针移动到初始位置
dataPoint = f.readlines()
for line in dataPoint:
    nameIndex = line.find('<Placemark>')
    if(nameIndex != -1):#找到了题头
        StartLoop = 1
        
    if(StartLoop):
        if(nameNotFound):
            nameIndexBegin = line.find('<name>')
            nameIndexEnd = line.find('</name>')
            if(nameIndexBegin != -1):
                name = line[nameIndexBegin+len('<name>'):nameIndexEnd]
                nameNotFound = 0
        elif((not nameNotFound) and posNotFound):
            posIndexBegin = line.find('<coordinates>')
            posIndexEnd = line.find('</coordinates>')
            if(posIndexBegin != -1):
                pos = line[posIndexBegin+len('<coordinates>'):posIndexEnd]
                outputData[name]=pos.split(',')
                posNotFound = 0
        else:
            posNotFound = 1
            nameNotFound = 1

f.close()
for item in outputData:
    print(item + ':' + outputData[item][0] + ',' + outputData[item][1] + ',' + outputData[item][2])
    fw.write(item + ':' + outputData[item][0] + ',' + outputData[item][1] + ',' + outputData[item][2] + '\n')        
fw.close()





