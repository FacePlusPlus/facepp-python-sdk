#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# $File: hello.py

# In this tutorial, you will learn how to call Face ++ APIs and implement a
# simple App which could recognize a face image in 3 candidates.
# 在本教程中，您将了解到Face ++ API的基本调用方法，并实现一个简单的App，用以在3
# 张备选人脸图片中识别一个新的人脸图片。

# You need to register your App first, and enter you API key/secret.
# 您需要先注册一个App，并将得到的API key和API secret写在这里。
API_KEY = '<your API key here>'
API_SECRET = '<your API secret here>'

# Import system libraries and define helper functions
# 导入系统库并定义辅助函数
import time
from pprint import pformat
def print_result(hint, result):
    def encode(obj):
        if type(obj) is unicode:
            return obj.encode('utf-8')
        if type(obj) is dict:
            return {encode(k): encode(v) for (k, v) in obj.iteritems()}
        if type(obj) is list:
            return [encode(i) for i in obj]
        return obj
    print hint
    result = encode(result)
    print '\n'.join(['  ' + i for i in pformat(result, width = 75).split('\n')])

# First import the API class from the SDK
# 首先，导入SDK中的API类
from facepp import API

api = API(API_KEY, API_SECRET)

# Here are the person names and their face images
# 人名及其脸部图片
IMAGE_DIR = 'http://cn.faceplusplus.com/static/resources/python_demo/'
PERSONS = [
    ('Jim Parsons', IMAGE_DIR + '1.jpg'),
    ('Leonardo DiCaprio', IMAGE_DIR + '2.jpg'),
    ('Andy Liu', IMAGE_DIR + '3.jpg')
]
TARGET_IMAGE = IMAGE_DIR + '4.jpg'

# Step 1: Detect faces in the 3 pictures and find out their positions and
# attributes
# 步骤1：检测出三张输入图片中的Face，找出图片中Face的位置及属性

FACES = {name: api.detection.detect(url = url)
        for name, url in PERSONS}

for name, face in FACES.iteritems():
    print_result(name, face)


# Step 2: create persons using the face_id
# 步骤2：引用face_id，创建新的person
for name, face in FACES.iteritems():
    rst = api.person.create(
            person_name = name, face_id = face['face'][0]['face_id'])
    print_result('create person {}'.format(name), rst)

# Step 3: create a new group and add those persons in it
# 步骤3：.创建Group，将之前创建的Person加入这个Group
rst = api.group.create(group_name = 'test')
print_result('create group', rst)
rst = api.group.add_person(group_name = 'test', person_name = FACES.iterkeys())
print_result('add these persons to group', rst)

# Step 4: train the model
# 步骤4：训练模型
rst = api.train.identify(group_name = 'test')
print_result('train', rst)
# wait for training to complete
# 等待训练完成
rst = api.wait_async(rst['session_id'])
print_result('wait async', rst)

# Step 5: recognize face in a new image
# 步骤5：识别新图中的Face
rst = api.recognition.identify(group_name = 'test', url = TARGET_IMAGE)
print_result('recognition result', rst)
print '=' * 60
print 'The person with highest confidence:', \
        rst['face'][0]['candidate'][0]['person_name']

# Finally, delete the persons and group because they are no longer needed
# 最终，删除无用的person和group
api.group.delete(group_name = 'test')
api.person.delete(person_name = FACES.iterkeys())

# Congratulations! You have finished this tutorial, and you can continue
# reading our API document and start writing your own App using Face++ API!
# Enjoy :)
# 恭喜！您已经完成了本教程，可以继续阅读我们的API文档并利用Face++ API开始写您自
# 己的App了！
# 旅途愉快 :)
