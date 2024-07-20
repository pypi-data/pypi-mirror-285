import tkinter as tk
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
from tkinter.ttk import *
from tkinter import*
from PIL import Image, ImageTk, ImageFont, ImageDraw
from time import time
from qrcode import make
import threading
from functools import partial
import cv2
import numpy as np

class myLabel(tk.Label):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        # self.font = ImageFont.truetype(font='', size=20)

    def show_image(self, img):
        #cv2类型图片转pillow类型图片
        img_pil = Image.fromarray(img)
        #图片缩放
        img_pil_res = img_pil.resize((640,360))

        #基于原始图像计算红色矩形框的坐标
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_red = np.array([0, 100, 100])
        upper_red = np.array([10, 255, 255])
        mask = cv2.inRange(hsv, lower_red, upper_red)

        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # 寻找红色物体的轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        max_area = 0
        max_contour = None
        for contour in contours:
            # 计算当前轮廓的面积
            area = cv2.contourArea(contour)
            # 如果当前轮廓的面积大于之前的最大面积，则更新最大轮廓和最大面积
            if area > max_area:
                max_area = area
                max_contour = contour

        # 计算轮廓的边界框
        if max_contour is not None:
            x, y, w, h = cv2.boundingRect(max_contour)
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            # cv2.imshow('Result', img)

            #在脸部矩形框中心绘制圆点
            draw = ImageDraw.Draw(img_pil_res)
            cx = x/2 + w/4
            cy = y/2 + h/4
            draw.ellipse((cx-5, cy-5, cx+5, cy+5), fill=(255,0,0))
            text = "( " + str(int(x+w/2)) + " , " + str(int(y+h/2)) + " )"
            draw.text((cx, cy), text, fill=(255, 0, 0))

        #把图片绘制到label上
        self.imgtk = ImageTk.PhotoImage(image=img_pil_res)
        self.configure(image=self.imgtk)


pwd = ''
root = ''
def tk_init(txt=''):
    global pwd,root
    pwd = ''
    root = tk.Tk()
    # 创建一个Label组件
    label = tk.Label(root,text=txt,bg='white')
    #root.iconphoto(False,'pwd.png')
    root.title('')
    label.pack()
    root.geometry("300x120+500+140")
    root.resizable(width=False, height=False)
    root.configure(bg='white')

def input_text(txt=''):
    tk_init(txt)
    def get_pwd():
       global pwd
       pwd = password_entry.get()
       #root.destroy()
       #print(pwd)
       root.destroy()
       #return pwd
    def on_close():
        global pwd
        pwd = ''
        root.destroy()

    password_entry = tk.Entry(root, show="",bd=5,width=35)
    password_entry.pack()
    ensureButton = Button(root, text ="确定", command = get_pwd)
    ensureButton.pack(padx = 25,ipadx=10,side='left')
    cancleButton = Button(root,text='取消',command=on_close)
    cancleButton.pack(padx = 25,ipadx=10,side='right')
    # 创建一个Entry组件，设置显示形式为星号
    # 运行主循环
    try:
        mainloop()
    except:
        pass
    return str(pwd)

def get_value():
    return str(pwd)

# pygame窗口显示文本方法
def draw_text(screen, text, pos, mark=0):
    # 设置文本框的外观
    text_box_rect = pygame.Rect(pos, (100, 40))
    text_layer = pygame.Surface(pos, pygame.SRCALPHA)
    text_layer.fill((255, 255, 255, 0))
    screen.blit(text_layer, pos)
    font = pygame.font.Font(None, 55)
    text_surface = font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=text_box_rect.center)
    screen.blit(text_surface, text_rect)
    pygame.display.update()

# tk创建窗口方法
def create_win(title, size):
    # 创建显示窗口

    win = tk.Tk()
    # 设置窗口标题
    win.title(title)
    # 设置窗口大小
    win.geometry('{}x{}'.format(size[0], size[1]))
    # 规定窗口不可缩放
    win.resizable(False, False)
    return win



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
        lb = myLabel(window,  bg=bg, font=('msyhbd.ttc', fz, 'bold'), text=text, anchor=anchor)
    else:
        lb = myLabel(win,  bg=bg,  font=('msyhbd.ttc', fz, 'bold'), text=text, anchor=anchor)
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

def generate_qrcode():
    global new_window
    
    new_window = tk.Toplevel()
    new_window.title("付款码")
    
    info = 'finished'
    qr_code_image = ImageTk.PhotoImage(make(info))
    qr_code_label = tk.Label(new_window, image=qr_code_image)
    qr_code_label.image = qr_code_image  # 保持引用，防止被垃圾回收
    qr_code_label.pack(pady=10)

def close_qrcode():
    new_window.destroy()

def show_button(button,pos):
    button.place(x=pos[0],y=pos[1])

def unshow_button(button):
    button.place_forget()

