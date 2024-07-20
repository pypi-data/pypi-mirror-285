import sys
#import re,os,time,json,string,logging,pymysql,webbrowser, random, inspect, urllib3, binascii, hashlib, datetime,glob,uuid
#import pandas as pd
#from appium.webdriver import webdriver
#from dbutils.pooled_db import PooledDB
#from operator import itemgetter
#from collections import OrderedDict
#from pathlib import Path

#from selenium import webdriver
#from collections.abc import Iterable,Iterator,ItemsView
#from geopy.distance import geodesic, distance
#from sshtunnel import SSHTunnelForwarder
#from screeninfo import get_monitors
#import request
#from watchdog.observers import Observer
#from watchdog.events import FileSystemEventHandler as FSEH

#PyQt相关
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon,QDesktopServices as QDS,QAction
from PyQt6.QtCore import QUrl

"""
PyQt相关
"""
# 设置窗体居中显示
def f_setcenter(self, w, h):
    # 获取主屏幕的信息
    from PyQt5.QtGui import QScreen
    screen = QApplication.primaryScreen()

    # 获取屏幕的分辨率（宽度和高度）
    screen_size = screen.size()

    # 计算窗口的初始位置（屏幕中心）
    width, height = 400, 300
    x = (screen_size.width() - width) // 2
    y = (screen_size.height() - height) // 2

    # 使用self.setGeometry()设置窗口的初始位置和大小
    self.setGeometry(x, y, width, height)
    x = (screen)
    pass


def f_exit(self, event):
    r0 = QMessageBox.question(self, "提示", "确定退出?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    if r0 == QMessageBox.StandardButton.Yes:
        r1 = QMessageBox.question(self, "提示", "再次确定退出?",
                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if r1 == QMessageBox.StandardButton.Yes:
            sys.exit()
        else:
            print('No')
    pass


class Filedialog(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        b_01 = QPushButton("OK", self)

        self.resize(800, 600)
        self.show()
        b_01.clicked.connect(self.f_ok)

    def f_ok(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Open file", '/', "Images(*.jpg *.gif)")
        print(fname)

    pass


# 关于
def f_msgabout(msg):
    QMessageBox.about('about', msg)
    pass


# 错误
def f_msgcritical(msg):
    QMessageBox.critical('Error', msg)
    pass


# 警告
def f_msgwarn(msg):
    QMessageBox.warning('Warn', msg)
    pass


# 消息
def f_msginfo(msg):
    QMessageBox.information('Info', msg)
    pass


# 询问
def f_msgquestion(msg):
    QMessageBox.question('Question', msg)
    pass


def f_openurl(self, url):
    QDS.openUrl(QUrl(url))
    pass


def f_add(a,b):
    return(a+b)
    pass
