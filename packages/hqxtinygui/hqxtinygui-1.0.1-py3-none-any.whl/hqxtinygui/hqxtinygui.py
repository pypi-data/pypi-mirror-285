import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor
import pygame
from tkinter.ttk import *
from tkinter import *
from PIL import Image, ImageTk, ImageFont, ImageDraw
import tkinter as tk

class InputDialog(QDialog):
    def __init__(self, prompt="", parent=None):
        super(InputDialog, self).__init__(parent)

        self.setStyleSheet("""
            QDialog {
                background-color: white;
                padding:0px;
                margin:0px;
            }
            QLineEdit {
                border-top: 5px solid gray;  /* 上边框 */
                border-left: 5px solid gray;
                border-right:5px solid #CCCCCC;
                border-bottom:5px solid #CCCCCC;
                padding: 5px;
            }
            QPushButton {
                border-top: 3px solid #CCCCCC;  /* 上边框 */
                border-left: 3px solid #CCCCCC;
                border-right:3px solid gray;
                border-bottom:3px solid gray;
                min-width: 80px;
                padding: 5px;
                background-color:#CCCCCC;
            }
            QPushButton:pressed {
                background-color: white;
            }
        """)

        self.setWindowTitle("输入框")
        self.setFixedSize(QSize(500,180))

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)  # 设置组件之间的间距为20像素

        # 添加间距
        self.main_layout.addSpacing(-30)
        self.prompt_label = QLabel(prompt, alignment=Qt.AlignCenter)
        self.prompt_label.setStyleSheet('margin-top:0px;')
        self.main_layout.addWidget(self.prompt_label)
        #添加间距
        self.main_layout.addSpacing(0)

        self.input_line_edit = QLineEdit(self)
        self.input_line_edit.setMinimumWidth(400)
        self.main_layout.addWidget(self.input_line_edit, alignment=Qt.AlignTop | Qt.AlignHCenter)

        #添加间距
        self.main_layout.addSpacing(15)
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignTop)

        self.ok_button = QPushButton("确定", self)
        self.cancel_button = QPushButton("取消", self)

        button_layout.addWidget(self.ok_button, alignment=Qt.AlignLeft)
        button_layout.addWidget(self.cancel_button, alignment=Qt.AlignRight)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        # 设置布局的外边距
        button_layout.setContentsMargins(40, 0, 40, 0)

        self.main_layout.addLayout(button_layout)

        self.setLayout(self.main_layout)

    def get_input(self):
        if self.exec_():
            return self.input_line_edit.text()
        else:
            return ""

def input_text(prompt=""):
    dialog = InputDialog(prompt=prompt)
    result = dialog.get_input()
    dialog.close()
    return result

import sys
app = QApplication(sys.argv)

def set_photo(path,win):
    image = Image.open(path)
    photo = ImageTk.PhotoImage(image)
    label = tk.Label(win,image=photo)
    label.image = photo
    label.place(x=0, y=0)

def create_root(size=(600,400), title='小河狸程序',  path=''):
    # 创建显示窗口
    global win
    win = tk.Tk()
    # 设置窗口标题
    win.title(title)
    # 设置窗口大小
    win.geometry('{}x{}'.format(size[0], size[1]))
    # 规定窗口不可缩放
    win.resizable(False, False)
    if path:
        set_photo(path, win)
    return win

def create_sub(root, size=(600,400), title='小河狸程序',  path=''):
    # 设置所属主窗口
    new_window =  tk.Toplevel(root)
    new_window.title(title)
    new_window.geometry('{}x{}'.format(size[0], size[1]))
    # 规定窗口不可缩放
    new_window.resizable(False, False)
    if path:
        set_photo(path, new_window)
    return new_window


#  tk创建标签方法
def create_label(window=None, pos=None, size=(100,40), text='标签',  bg='yellow', anchor='center', fz=12):
    global id
    if window:
        lb = tk.Label(window,  bg=bg, font=('msyhbd.ttc', fz, 'bold'), text=text, anchor=anchor)
    else:
        lb = tk.Label(win,  bg=bg,  font=('msyhbd.ttc', fz, 'bold'), text=text, anchor=anchor)
    if pos == None:
        pos = (id*100, 0)
        id += 1 
    lb.place(x=pos[0], y=pos[1], width=size[0], height=size[1])
    return lb

# tk创建按钮方法
def create_button( window=None, pos=None, size=(100,40), text='按钮', fz=14):
    global id
    if window:
        btn = tk.Button(window, text=text, font=('msyhbd.ttc', fz, 'bold'))
    else:
        btn = tk.Button(win, text=text, font=('msyhbd.ttc', fz, 'bold'))
    if pos == None:
        pos = (id*100, 0)
        id += 1
    btn.place(x=pos[0], y=pos[1], width=size[0], height=size[1])
    return btn

# tk创建输入框方法
def create_entry(win, pos, size, text='',  fz=18):
    string = tk.StringVar()
    ety = tk.Entry(win, text=text, font=('msyh.ttc', fz), textvariable=string)
    ety.place(x=pos[0], y=pos[1], width=size[0], height=size[1])
    return ety

