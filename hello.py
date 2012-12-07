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
PERSONS = [
    ('Brad Pitt', 'http://www.faceplusplus.com/static/img/demo/9.jpg'),
    ('Nicolas Cage', 'http://www.faceplusplus.com/static/img/demo/7.jpg'),
    ('Jackie Chan', 'http://www.faceplusplus.com/static/img/demo/6.jpg')
]
TARGET_IMAGE = 'http://www.faceplusplus.com/static/img/demo/13.jpg'

# Step 1: Create a group to add these persons in
# 步骤1： 新建一个group用以添加person
api.group.create(group_name = 'test')

# Step 2: Detect faces from those three images and add them to the persons
# 步骤2：从三种图片中检测人脸并将其加入person中。 
for (name, url) in PERSONS:
    result = api.detection.detect(url = url, mode = 'oneface')
    print_result('Detection result for {}:'.format(name), result)

    face_id = result['face'][0]['face_id'] 

    # Create a person in the group, and add the face to the person
    # 在该group中新建一个person，并将face加入期中
    api.person.create(person_name = name, group_name = 'test',
            face_id = face_id)


# Step 3: Train the group.
# Note: this step is required before performing recognition in this group,
# since our system needs to pre-compute models for these persons
# 步骤3：训练这个group
# 注：在group中进行识别之前必须执行该步骤，以便我们的系统能为这些person建模
result = api.recognition.train(group_name = 'test', type = 'all')

# Because the train process is time-consuming, the operation is done
# asynchronously, so only a session ID would be returned.
# 由于训练过程比较耗时，所以操作必须异步完成，因此只有session ID会被返回
print_result('Train result:', result)

session_id = result['session_id']

# Now, wait before train completes
# 等待训练完成
while True:
    result = api.info.get_session(session_id = session_id)
    if result['status'] == u'SUCC':
        print_result('Async train result:', result)
        break
    time.sleep(1)

#也可以通过调用api.wait_async(session_id)函数完成以上功能


# Step 4: recognize the unknown face image
# 步骤4：识别未知脸部图片
result = api.recognition.recognize(url = TARGET_IMAGE, group_name = 'test')
print_result('Recognize result:', result)
print '=' * 60
print 'The person with highest confidence:', \
        result['face'][0]['candidate'][0]['person_name']


# Finally, delete the persons and group because they are no longer needed
# 最终，删除无用的person和group
api.group.delete(group_name = 'test')
api.person.delete(person_name = [i[0] for i in PERSONS])

# Congratulations! You have finished this tutorial, and you can continue
# reading our API document and start writing your own App using Face++ API!
# Enjoy :)
# 恭喜！您已经完成了本教程，可以继续阅读我们的API文档并利用Face++ API开始写您自
# 己的App了！
# 旅途愉快 :)
