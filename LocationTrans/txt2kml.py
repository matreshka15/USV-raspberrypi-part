#!/usr/bin/env python
# coding: utf-8

# In[142]:


fw = open("MapDataOutput1.kml","w+")
f = open("LatLong.txt","r")
test = open("CONFIGURE/Basis.kml","r")  #open("CONFIGURE/t.kml","r")#,encoding='gb18030',errors='ignore')


# In[143]:


for line in test:
    state = line.find("<Placemark>")
    if(state == -1):
        fw.write(line)
    else:
        break


# In[144]:


f.seek(0,0)
for line in f:
    spliter = line.find(":")
    name = line[:spliter]
    spliter_latlon = line.find(",")
    lon = line[spliter+1:spliter_latlon]
    line =line[spliter_latlon+1:]
    spliter_latlon = line.find(",")
    lat = line[:spliter_latlon]
    print( "\t\t\t<Placemark>\n\t\t\t<name>{0}</name>\n\t\t\t<LookAt>\n\t\t\t\t<longitude>{1}</longitude>\n\t\t\t\t<latitude>{2}</latitude>\n\t\t\t\t<altitude>0</altitude>\n\t\t\t\t<heading>0</heading>\n\t\t\t\t<tilt>0</tilt>\n\t\t\t\t<range>728.8612258819933</range>\n\t\t\t\t<gx:altitudeMode>relativeToSeaFloor</gx:altitudeMode>\n\t\t\t\t</LookAt>\n\t\t\t\t<styleUrl>#m_ylw-pushpin</styleUrl>\n\t\t\t<Point>\n\t\t\t\t<gx:drawOrder>1</gx:drawOrder>\n\t\t\t\t<coordinates>{1},{2},0</coordinates>\n\t\t\t\t</Point>\n\t\t\t</Placemark>\n".format(name,lon,lat),file=fw)
    print("name:%s lat:%s lon:%s"%(name,lon,lat))


# In[145]:


print("</Folder>\n</Document>\n</kml>\n",file=fw)
fw.close()
f.close()
test.close()


# In[146]:


fw = open("MapDataOutput1.kml","r")
for line in fw:
    print(line)


# In[147]:


fw.close()


# In[ ]:




