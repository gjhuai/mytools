#!/usr/bin/env python
#-*- coding: utf-8 -*-
from ftplib import FTP       #调用 模块
import sys,getpass,os.path   #调用 模块
host = '192.168.31.200'       #ftp地址
port = 21              #端口号
timenout = 30                #超时时间
username = 'gjh'           #ftp用户名
password = 'hbdl9431'          #ftp 密码
localfile = 'b.txt'   #本机要上传的文件与路径
remotepath = '/syncftp'       #ftp服务器的路径 (ftp://192.168.1.101/share)
f = FTP()
f.connect(host,port,timenout)  #连接ftp服务器
f.login(username,password)     #登录ftp服务器
f.cwd(remotepath+"sss")              #设置ftp服务器端的路径
# file = open(localfile,'rb')    #打开本地文件
# f.storbinary('STOR %s' % os.path.basename(localfile),file)  #上传文件到ftp服务器
# file.close()   #关闭本地文件
f.quit()       #退出