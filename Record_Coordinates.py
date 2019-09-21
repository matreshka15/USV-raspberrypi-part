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

#记录点函数
#传入参数：
#startbit:记录点标志位；
#file:打开的文件
#index:写入点的索引号
def start(file,index,longtitude,latitude,height):
    #print(index + ':' + longtitude + ',' + latitude + ',' + height + '\n')
    file.write(str(index) + ':' + str(longtitude) + ',' + str(latitude) + ',' + str(height) + '\n')



