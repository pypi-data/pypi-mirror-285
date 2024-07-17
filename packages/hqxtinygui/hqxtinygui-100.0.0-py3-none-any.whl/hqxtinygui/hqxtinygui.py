from tkinter.ttk import *
from tkinter import *
from PIL import Image, ImageTk, ImageDraw, ImageFont
import tkinter as tk


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
    new_window = tk.Toplevel(root)
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