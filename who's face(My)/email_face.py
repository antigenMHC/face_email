#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    * @version      V1.0
    @author: antigenMHC
"""


from __future__ import division
import cv2
import importlib
import time  
import signal  
import sys
importlib.reload(sys)

import smtplib                                  #引入SMTP协议包
from email.mime.text import MIMEText
from email.header import Header
from email.mime.multipart import MIMEMultipart  #创建包含多个部分的邮件体
from email.mime.base import MIMEBase            #添加附件（附件内容并附加到根容器 ）
from email.mime.image import MIMEImage
import os.path                                  #分析路径
from email import encoders
import requests
import base64
import json
from aip import AipFace
from aip import AipSpeech
import pygame
import time


""" 你的 APPID AK SK """
APP_ID = 'xxxxxx'
API_KEY = 'xxxxxxxx'
SECRET_KEY = 'xxxxxxxx'
client = AipFace(APP_ID, API_KEY, SECRET_KEY)
aipSpeech=AipSpeech(APP_ID,API_KEY,SECRET_KEY)

sendDate=0
sender = "your@qq.com"                     #发送邮箱，qq邮箱
password = "xxxxxxxx"                      #开启SMTP服务获得的密钥
receiver = "your@qq.com"                  #目标邮箱
#--------------------邮件服务与端口信息----------------------
smtp_server = "smtp.qq.com"
smtp_port = 465                                 #qq的SMTP端口465
msg = MIMEMultipart('related')                  #采用related定义内嵌资源的邮件体

cap = cv2.VideoCapture(0)
cap.set(3, 480)
cap.set(4, 320)
#比较器 xml的位置
pathf = 'D:\\untitled3\\OpenCv\\email_face\\123.xml'
face_cascade = cv2.CascadeClassifier(pathf)
face_cascade.load(pathf)

'''client id即API_KEY， client secret即你的API_secret '''
api1="https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=xxxxxxx&client_secret=xxxxxxx"

def get_token():
    response=requests.get(api1)
    access_token=eval(response.text)['access_token']
    api2="https://aip.baidubce.com/rest/2.0/face/v3/match"+"?access_token="+access_token
    return api2

# 3,读取图片数据
def read_img(img1,img2):
    with open(img1,'rb') as f:
        pic1=base64.b64encode(f.read())
    with open(img2,'rb') as f:
        pic2=base64.b64encode(f.read())
    params=json.dumps([
        {"image":str(pic1,"utf-8"),"image_type":'BASE64',"face_type":"LIVE"},
        {"image":str(pic2,"utf-8"),"image_type":'BASE64',"face_type":"IDCARD"}
    ])
    return params

def analyse_img(file1,file2):
    params=read_img(file1,file2)
    api=get_token()
    content=requests.post(api,params).text
    #print(content)
    score=eval(content)['result']['score']
    return score

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


def fileopen(filepath): #打开图片
    with open(filepath, 'rb') as f:
        data = base64.b64encode(f.read())
    image = str(data,'utf-8')
    return image

def loud():
    pygame.mixer.init()
    pygame.mixer.music.load('audio.mp3')
    pygame.mixer.music.play()
    time.sleep(1)
    pygame.mixer.music.stop()

while True:  
    ret,frame = cap.read()
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    time.sleep(4)
    faces = face_cascade.detectMultiScale( gray )
    max_face = 0
    value_x = 0
    font=cv2.FONT_HERSHEY_SIMPLEX
    #记录拍摄的时间
    cv2.putText(frame,time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),(20,20),font,0.8,(255,255,255),1)
    if len(faces)>0:
        print('这个人有脸!')
        currentDate=time.time()
        
        for (x,y,w,h) in faces:
            cv2.rectangle(frame,(x,y),(x+h,y+w),(0,255,0),2)#0,255,0
            #max_face=w*h
            result = (x,y,w,h)
            x=result[0]
            y = result[1]
        
        #避免在短时间内重复拍摄，设置时间戳
        if currentDate-sendDate>600:
            cv2.imwrite("out.png",frame)

            img_file = open('out.png', "rb")
            img_data = img_file.read()
            img_file.close()
            img = MIMEImage(img_data)

            score = analyse_img('test.png', 'out.png')
            if score<90:
                img.add_header('Content-ID', '0')    #正常附件的header是不同的
                msg.attach(img)
                msg["From"] = Header("antigenMHC", "utf-8")
                msg["To"] = Header(receiver, "utf-8")
                msg["Subject"] = Header("who are you", "utf-8")
                #-----------------将图片作为正文内容添加-------------------
                message = MIMEText("<p>woc!!!!!</p><p>有人在用你电脑</p><img src='cid:0'/>","html","utf-8")    #plain表示纯文本
                msg.attach(message)
                contype = 'application/octet-stream'
                maintype, subtype = contype.split('/', 1)
                try:
                    #qq必须要用.SMTP_SSL
                    #其他服务器try:.SMTP
                    smtpObject = smtplib.SMTP_SSL(smtp_server, smtp_port)
                    smtpObject.login(sender, password)
                    #message.as_string()是将MIMEText对象变成字符串
                    smtpObject.sendmail(sender, [receiver], msg.as_string())
                    print ("发送成功", '匹配率', score)

                    print(score)
                except smtplib.SMTPException :
                    print ("发送失败！")

                loud()          #语音震慑
                smtpObject.quit()
                sendDate=time.time()
            else:
                print('你就是我的master, 我不会警报的', "匹配率: ", score)
    cv2.imshow("capture", frame)
    if cv2.waitKey(1)==119:
        break

cap.release()
cv2.destroyAllWindows()
