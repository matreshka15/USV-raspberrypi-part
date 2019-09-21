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
import math

#测试通过
def DDD2DMS(number):
    D = number//1
    temp = number%1
    M = (temp*60)//1
    temp = (temp*60) %1
    S = (temp*60)
    return D+(M/100)+(S/10000)

#测试通过
def angleFromCoordinate(long1, lat1, long2, lat2):
    lat1 = math.radians(DDD2DMS(lat1))
    lat2 = math.radians(DDD2DMS(lat2))
    long1 = math.radians(DDD2DMS(long1))
    long2 = math.radians(DDD2DMS(long2))
    y = math.sin(long2-long1)*math.cos(lat2)
    x = math.cos(lat1)*math.sin(lat2)-math.sin(lat1)*math.cos(lat2)*math.cos(long2-long1)
    deltaLon = long2-long1
    theta = math.atan2(y,x)
    theta = math.degrees(theta)
    theta = (theta+360)%360
    return theta

def distanceFromCoordinate(lon1, lat1, lon2, lat2): # 经度1，纬度1，经度2，纬度2 （十进制度数）
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
 
    # haversine公式
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # 地球平均半径，单位为公里
    return c * r * 1000 *100

temp = angleFromCoordinate(120.5139651439754,36.89759065531443,120.5147411312813,36.89198937216152)
print(temp)
temp = distanceFromCoordinate(120.5139651439754,36.89759065531443,120.5147411312813,36.89198937216152)
print(temp)
