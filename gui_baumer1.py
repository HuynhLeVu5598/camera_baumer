from copyreg import remove_extension
from faulthandler import disable
import glob
import os
import cv2
import threading
import torch
import numpy as np 
import time

import PySimpleGUI as sg

from PIL import Image,ImageTk
import os
import datetime 
import shutil

from PIL import Image

from udp import UDPFinsConnection
from initialization import FinsPLCMemoryAreas

import traceback

import neoapi


#CAM 1   2048x1536              192.168.25.2
#CAM 2   1440x1080              169.254.139.50


# SCALE_X_CAM1 = 1/3.2
# SCALE_Y_CAM1 = 1/3.2

# SCALE_X_CAM2 = 1/2.25
# SCALE_Y_CAM2 = 1/2.25


# SCALE_X_CAM1 = 640/2048
# SCALE_Y_CAM1 = 480/1536

mysleep = 0.1

SCALE_X_CAM1 = 640*1.2/2048
SCALE_Y_CAM1 = 480*1.2/1536

SCALE_X_CAM2 = 640/1440
SCALE_Y_CAM2 = 480/1080

def connect_plc(host):
    global fins_instance
    try:
        fins_instance = UDPFinsConnection()
        fins_instance.connect(host)
        fins_instance.dest_node_add=1
        fins_instance.srce_node_add=25

        return True
    except:
        print("Can't connect to PLC")
        for i in range(100000000):
            pass
        #sleep(3)
        print("Reconnecting....")
        return False

def time_to_name():
    current_time = datetime.datetime.now() 
    name_folder = str(current_time)
    name_folder = list(name_folder)
    for i in range(len(name_folder)):
        if name_folder[i] == ':':
            name_folder[i] = '-'
        if name_folder[i] == ' ':
            name_folder[i] ='_'
        if name_folder[i] == '.':
            name_folder[i] ='-'
    name_folder = ''.join(name_folder)
    return name_folder


def load_param_model(filename):
    list_param_model = []
    with open(filename) as lines:
        for line in lines:
            _, value = line.strip().split('=')
            list_param_model.append(value)
    return list_param_model


def save_param_model1_A22(weight,size,conf,nut_me,divat,me,namchamcao,traybactruc,divatduoi,kimcaomax,kimcaomin):
    line1 = 'weights1' + '=' + str(weight)
    line3 = 'size1' + '=' + str(size)
    line4 = 'conf1' + '=' + str(conf)
    line5 = 'nut_me1' + '=' + str(nut_me)
    line6 = 'divat1' + '=' + str(divat)
    line7 = 'me1' + '=' + str(me)
    line8 = 'namchamcao1' + '=' + str(namchamcao)
    line9 = 'traybactruc1' + '=' + str(traybactruc)
    line10 = 'divatduoi1' + '=' + str(divatduoi)
    line11 = 'kimcaomax1' + '=' + str(kimcaomax)
    line12 = 'kimcaomin1' + '=' + str(kimcaomin)

    lines = [line1,line3,line4,line5,line6,line7,line8,line9,line10,line11,line12]
    with open('static/param_model1_A22.txt', "w") as f:
        for i in lines:
            f.write(i)
            f.write('\n')

def save_param_model1_A19(weight,size,conf,nut_me,divat,me,namchamcao,traybactruc,divatduoi,kimcaomax,kimcaomin):
    line2 = 'weights1' + '=' + str(weight)
    line3 = 'size1' + '=' + str(size)
    line4 = 'conf1' + '=' + str(conf)
    line5 = 'nut_me1' + '=' + str(nut_me)
    line6 = 'divat1' + '=' + str(divat)
    line7 = 'me1' + '=' + str(me)
    line8 = 'namchamcao1' + '=' + str(namchamcao)
    line9 = 'traybactruc1' + '=' + str(traybactruc)
    line10 = 'divatduoi1' + '=' + str(divatduoi)
    line11 = 'kimcaomax1' + '=' + str(kimcaomax)
    line12 = 'kimcaomin1' + '=' + str(kimcaomin)

    lines = [line2,line3,line4,line5,line6,line7,line8,line9,line10,line11,line12]
    with open('static/param_model1_A19.txt', "w") as f:
        for i in lines:
            f.write(i)
            f.write('\n')

def save_param_model2_A22(weight,size,conf,nut_me,divat,me):
    line1 = 'weights2' + '=' + str(weight)
    line3 = 'size2' + '=' + str(size)
    line4 = 'conf2' + '=' + str(conf)
    line5 = 'nut_me2' + '=' + str(nut_me)
    line6 = 'divat2' + '=' + str(divat)
    line7 = 'me2' + '=' + str(me)

    lines = [line1,line3,line4,line5,line6,line7]
    with open('static/param_model2_A22.txt', "w") as f:
        for i in lines:
            f.write(i)
            f.write('\n')

def save_param_model2_A19(weight,size,conf,nut_me,divat,me):
    line1 = 'weights2' + '=' + str(weight)
    line3 = 'size2' + '=' + str(size)
    line4 = 'conf2' + '=' + str(conf)
    line5 = 'nut_me2' + '=' + str(nut_me)
    line6 = 'divat2' + '=' + str(divat)
    line7 = 'me2' + '=' + str(me)

    lines = [line1,line3,line4,line5,line6,line7]
    with open('static/param_model2_A19.txt', "w") as f:
        for i in lines:
            f.write(i)
            f.write('\n')

def load_theme():
    name_themes = []
    with open('static/theme.txt') as lines:
        for line in lines:
            _, name_theme = line.strip().split(':')
            name_themes.append(name_theme)
    return name_themes

def save_theme(name_theme):
    line = 'theme:' + name_theme
    with open('static/theme.txt','w') as f:
        f.write(line)


def load_choose_model():
    name_models = []
    with open('static/choose_model.txt') as lines:
        for line in lines:
            _, name_model = line.strip().split(':')
            name_models.append(name_model)
    return name_models[0]

def save_choose_model(name_model):
    line = 'choose_model:' + name_model
    with open('static/choose_model.txt','w') as f:
        f.write(line)

def load_param_camera1():
    list_param_camera1 = []
    with open('static/param_camera1.txt') as lines:
        for line in lines:
            _,value = line.strip().split(':')
            list_param_camera1.append(value)
    return list_param_camera1

def load_param_camera2():
    list_param_camera2 = []
    with open('static/param_camera2.txt') as lines:
        for line in lines:
            _,value = line.strip().split(':')
            list_param_camera2.append(value)
    return list_param_camera2

def save_param_camera1(v1,v2,v3,v4,v5):
    line1 = 'exposure1:' + str(v1)
    line2 = 'gain1:' + str(v2)
    line3 = 'red1:' + str(v3)
    line4 = 'green1:' + str(v4)
    line5 = 'blue1:' + str(v5)

    lines = [line1,line2,line3,line4,line5]
    with open('static/param_camera1.txt', "w") as f:
        for i in lines:
            f.write(i)
            f.write('\n')

def save_param_camera2(v1,v2):
    line1 = 'exposure2:' + str(v1)
    line2 = 'gain2:' + str(v2)
    lines = [line1,line2]
    with open('static/param_camera2.txt', "w") as f:
        for i in lines:
            f.write(i)
            f.write('\n')



def task_camera1(model,size,conf):
    read_2000 = fins_instance.memory_area_read(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x07\xD0\x00') # doc thanh ghi 2000
    #print('cam1')
    #print(read_2000[-1:])
    temp1 = 1
    if temp1==1 and read_2000 == b'\xc0\x00\x02\x00\x19\x00\x00\x01\x00`\x01\x01\x00@\x00%':  # gia tri 37

        print('CAM 1')
        t1 = time.time()
        
        img1_orgin = camera1.GetImage().GetNPArray()
        img1_orgin = img1_orgin[50:530,70:710]
        img1_orgin = img1_orgin.copy()

        # ghi vao D2000 gia tri 0
        fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x07\xD0\x00',b'\x00\x00',1)


        img1_convert = cv2.cvtColor(img1_orgin, cv2.COLOR_BGR2RGB)

        result1 = model(img1_convert,size= size,conf = conf) 
        t2 = time.time() - t1
        print(t2) 
        #time.sleep(10)
        table1 = result1.pandas().xyxy[0]
        area_remove1 = []
        for item in range(len(table1.index)):
            width1 = table1['xmax'][item] - table1['xmin'][item]
            height1 = table1['ymax'][item] - table1['ymin'][item]
            area1 = width1*height1
            if table1['name'][item] == 'nut_me':
                if area1 < values['area_nutme1_a22']: 
                    table1.drop(item, axis=0, inplace=True)
                    area_remove1.append(item)

            elif table1['name'][item] == 'divat':
                if area1 < values['area_divat1_a22']: 
                    table1.drop(item, axis=0, inplace=True)
                    area_remove1.append(item)

            elif table1['name'][item] == 'me':
                if area1 < values['area_me1_a22']: 
                    table1.drop(item, axis=0, inplace=True)
                    area_remove1.append(item)

            elif table1['name'][item] == 'namchamcao':
                if height1 < values['y_namchamcao1_a22']: 
                    table1.drop(item, axis=0, inplace=True)
                    area_remove1.append(item)

            elif table1['name'][item] == 'tray_bac_truc':
                if area1 < values['area_traybactruc1_a22']: 
                    table1.drop(item, axis=0, inplace=True)
                    area_remove1.append(item)

            elif table1['name'][item] == 'di_vat_duoi':
                if area1 < values['area_divatduoi1_a22']: 
                    table1.drop(item, axis=0, inplace=True)
                    area_remove1.append(item)

            elif table1['name'][item] == 'kimcao':
                if height1 < values['ymin_kimnamcham1_a22']: 
                    table1.drop(item, axis=0, inplace=True)
                    area_remove1.append(item)
                elif height1 > values['ymax_kimnamcham1_a22']: 
                    table1.drop(item, axis=0, inplace=True)
                    area_remove1.append(item)

        names1 = list(table1['name'])
        print(names1)

        len_ncc = 0
        for ncc in names1:
            if ncc == 'namchamcao':
                len_ncc +=1
        
        len_kimcao = 0
        for kimcao in names1:
            if kimcao == 'kimcao':
                len_kimcao += 1

        save_memorys1 = []

        if 'tray_bac_truc' in names1 or 'di_vat_duoi' in names1:
            save_memorys1.append(1000)
        if 'kimnamcham' not in names1 or len_kimcao !=2:
            save_memorys1.append(1002)
        if 'divat' in names1 or 'me' in names1 or 'nut_me' in names1 or 'nut' in names1 or len_ncc !=2:
            save_memorys1.append(1004)

        time.sleep(mysleep)

        for save_memory1 in save_memorys1:
            # bac_truc
            if save_memory1 == 1000: 
                # ghi vao D1000 gia tri 1 
                fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xE8\x00',b'\x00\x01',1)
                # ghi vao D1006 (03EE) gia tri 2 => khong ok
                #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xEE\x00',b'\x00\x02',1)
            # kim nam cham
            if save_memory1 == 1002:
                # ghi vao D1002 gia tri 1 
                fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xEA\x00',b'\x00\x01',1)
                # ghi vao D1006 (03EE) gia tri 2 => khong ok
                #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xEE\x00',b'\x00\x02',1)

            #nam cham
            if save_memory1 == 1004:
                # ghi vao D1004 gia tri 1 
                fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xEC\x00',b'\x00\x01',1)
                # ghi vao D1006 gia tri 2 => khong ok
                #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xEE\x00',b'\x00\x02',1)

            #OK
        if len(save_memorys1) == 0:
            # ghi vao D1006 gia tri 1 
            fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xEE\x0B',b'\x00\x01',1)
            # ghi vao D1000 gia tri 2
            #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xE8\x00',b'\x00\x02',1)
            # ghi vao D1002 gia tri 2
            #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xEA\x00',b'\x00\x02',1)
            # ghi vao D1004 gia tri 2
            #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xEC\x00',b'\x00\x02',1)             

        #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x07\xD0\x00',b'\x00\x04',1)
        t2 = time.time() - t1
        print(t2) 
        time_cam1 = str(int(t2*1000)) + 'ms'
        window['time_cam1'].update(value= time_cam1, text_color='black') 


        show1 = np.squeeze(result1.render(area_remove1))
        show1 = cv2.resize(show1, (image_width_display,image_height_display), interpolation = cv2.INTER_AREA)

        if 'kimnamcham' not in names1 or len_ncc !=2 or len_kimcao !=2 \
        or 'divat' in names1 or 'me' in names1 or 'nut_me' in names1 or 'nut' in names1 \
        or 'tray_bac_truc' in names1 or 'di_vat_duoi' in names1:
            print('NG')
            cv2.putText(show1, 'NG',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,0,255),5)
            window['result_cam1'].update(value= 'NG', text_color='red')
            name_folder_ng = time_to_name()
            cv2.imwrite('G:/result/Cam1/NG/' + name_folder_ng + '.jpg',img1_orgin)
            cv2.imwrite('G:/Windows/1/' + name_folder_ng + '.jpg',img1_orgin)
        else:
            print('OK')
            cv2.putText(show1, 'OK',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,255,0),5)
            window['result_cam1'].update(value= 'OK', text_color='green')
            name_folder_ok = time_to_name()
            cv2.imwrite('G:/result/Cam1/OK/' + name_folder_ok  + '.jpg',img1_orgin)
    

        imgbytes1 = cv2.imencode('.png',show1)[1].tobytes()
        window['image1'].update(data= imgbytes1)
        temp1=0
        print('---------------------------------------------')



def task_camera2(model,size,conf):
    read_2002 = fins_instance.memory_area_read(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x07\xD2\x00') # doc thanh ghi 2002
    #print('cam2')
    #print(read_2002[-1:])
    temp2 = 1
    if temp2 == 1 and read_2002 ==b'\xc0\x00\x02\x00\x19\x00\x00\x01\x00`\x01\x01\x00@\x00%':  # gia tri 37

        print('CAM 2')
        t1 = time.time()
        img2_orgin = camera2.GetImage().GetNPArray()
        #img2_orgin = cv2.cvtColor(img2_orgin, cv2.COLOR_BGR2RGB)

        # ghi vao D2002 gia tri 0
        fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x07\xD2\x00',b'\x00\x00',1)

        result2 = model(img2_orgin,size= size,conf = conf) 
        t2 = time.time() - t1
        print(t2) 

        table2 = result2.pandas().xyxy[0]

        area_remove2 = []
        for item in range(len(table2.index)):
            width2 = table2['xmax'][item] - table2['xmin'][item]
            height2 = table2['ymax'][item] - table2['ymin'][item]
            area2 = width2*height2
            if table2['name'][item] == 'nut_me':
                if area2 < values['area_nutme2_a22']: 
                    table2.drop(item, axis=0, inplace=True)
                    area_remove2.append(item)

            elif table2['name'][item] == 'divat':
                if area2 < values['area_divat2_a22']: 
                    table2.drop(item, axis=0, inplace=True)
                    area_remove2.append(item)

            elif table2['name'][item] == 'me':
                if area2 < values['area_me2_a22']: 
                    table2.drop(item, axis=0, inplace=True)
                    area_remove2.append(item)

        names2 = list(table2['name'])
        print(names2)

        save_memorys2 = []
        if 'namcham' not in names2 or 'divat' in names2 or 'me' in names2 or 'namchamcao' in names2 or 'nut_me' in names2 or 'nut' in names2:
            save_memorys2.append(1014)
        # thieu kimnamcham 1012 va bactruc 1010

        time.sleep(mysleep)

        for save_memory2 in save_memorys2:
            # bac_truc
            if save_memory2 == 1010: 
                # ghi vao D1010 gia tri 1 
                fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xF2\x00',b'\x00\x01',1)
                # ghi vao D1016 gia tri 2 => khong ok
                #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xF8\x00',b'\x00\x02',1)
            # kim nam cham
            if save_memory2 == 1012:
                # ghi vao D1012 gia tri 1 
                fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xF4\x00',b'\x00\x01',1)
                # ghi vao D1016 gia tri 2 => khong ok
                #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xF8\x00',b'\x00\x02',1)

            #nam cham
            if save_memory2 == 1014:
                # ghi vao D1014 gia tri 1 
                fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xF6\x00',b'\x00\x01',1)
                # ghi vao D1016 gia tri 2 => khong ok
                #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xF8\x00',b'\x00\x02',1)

        #OK
        if len(save_memorys2) == 0:
            # ghi vao D1016 gia tri 1 
            fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xF8\x0B',b'\x00\x01',1)
            # ghi vao D1010 gia tri 2
            #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xF2\x00',b'\x00\x02',1)
            # ghi vao D1012 gia tri 2
            #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xF4\x00',b'\x00\x02',1)
            # ghi vao D1014 gia tri 2
            #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xF6\x00',b'\x00\x02',1)             

        #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x07\xD2\x00',b'\x00\x04',1)
        t2 = time.time() - t1
        print(t2) 
        time_cam2 = str(int(t2*1000)) + 'ms'
        window['time_cam2'].update(value= time_cam2, text_color='black') 

        show2 = np.squeeze(result2.render(area_remove2))
        show2 = cv2.resize(show2, (image_width_display,image_height_display), interpolation = cv2.INTER_AREA)

        if 'namcham' not in names2 \
        or 'divat' in names2 or 'me' in names2 or 'namchamcao' in names2 or 'nut_me' in names2 or 'nut' in names2:
            print('NG')
            cv2.putText(show2, 'NG',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,0,255),5)
            window['result_cam2'].update(value= 'NG', text_color='red')  
            name_folder_ng = time_to_name()
            cv2.imwrite('G:/result/Cam2/NG/' + name_folder_ng + '.jpg',img2_orgin)     
            cv2.imwrite('G:/Windows/2/' + name_folder_ng + '.jpg',img2_orgin)    
        else:
            print('OK')
            cv2.putText(show2, 'OK',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,255,0),5)
            window['result_cam2'].update(value= 'OK', text_color='green')
            name_folder_ok = time_to_name()
            cv2.imwrite('G:/result/Cam2/OK/' + name_folder_ok + '.jpg',img2_orgin)        


        imgbytes2 = cv2.imencode('.png',show2)[1].tobytes()
        window['image2'].update(data= imgbytes2)
        temp2 = 0
        print('---------------------------------------------')
        

def test_camera1(model,size,conf):
    read_2000 = fins_instance.memory_area_read(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x07\xD0\x00') # doc thanh ghi 2000
    if read_2000 ==b'\xc0\x00\x02\x00\x19\x00\x00\x01\x00`\x01\x01\x00@\x00%':  # gia tri 37
        print('CAM 1')
        t1 = time.time()
        img1_orgin = camera1.GetImage().GetNPArray()
        img1_orgin = img1_orgin[50:530,70:710]
        img1_orgin = img1_orgin.copy()
        img1_convert = cv2.cvtColor(img1_orgin, cv2.COLOR_BGR2RGB)
        result1 = model(img1_convert,size= size,conf = conf) 
        #img1_orgin = cv2.resize(img1_orgin,(640,480))


        # ghi vao D1006 gia tri 1 
        fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xEE\x0B',b'\x00\x01',1)
        # ghi vao D1000 gia tri 2
        #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xE8\x00',b'\x00\x02',1)
        # ghi vao D1002 gia tri 2
        #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xEA\x00',b'\x00\x02',1)
        # ghi vao D1004 gia tri 2
        #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xEC\x00',b'\x00\x02',1)             

        # ghi vao D2000 gia tri 0
        fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x07\xD0\x00',b'\x00\x00',1)


        show1 = np.squeeze(result1.render())
        show1 = cv2.resize(show1, (image_width_display,image_height_display), interpolation = cv2.INTER_AREA)


        print('OK')
        cv2.putText(show1, 'OK',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,255,0),5)
        window['result_cam1'].update(value= 'OK', text_color='green')
        
        name_folder_ok = time_to_name()
        cv2.imwrite('G:/result/Cam1/OK/' + name_folder_ok  + '.jpg',img1_orgin)


        imgbytes1 = cv2.imencode('.png',show1)[1].tobytes()
        window['image1'].update(data= imgbytes1)

        #print('---------------------------------------------')


        # name_folder_ok = time_to_name()
        # cv2.imwrite('G:/result/Cam1/OK/' + name_folder_ok  + '.jpg',img1_orgin)

        # img1_orgin = cv2.resize(img1_orgin,(image_width_display,480))
        # imgbytes1 = cv2.imencode('.png',img1_orgin)[1].tobytes()
        # window['image1'].update(data= imgbytes1)

        t2 = time.time() - t1
        print(t2) 

        print('---------------------------------------------')





def test_camera2():
    read_2002 = fins_instance.memory_area_read(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x07\xD2\x00') # doc thanh ghi 2002
    if read_2002 ==b'\xc0\x00\x02\x00\x19\x00\x00\x01\x00`\x01\x01\x00@\x00%':  # gia tri 37
        print('CAM 2')
        t1 = time.time()
        img2_orgin = camera2.GetImage().GetNPArray()


        # ghi vao D1016 gia tri 1 
        fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xF8\x0B',b'\x00\x01',1)
        # ghi vao D1010 gia tri 2
        #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xF2\x00',b'\x00\x02',1)
        # ghi vao D1012 gia tri 2
        #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xF4\x00',b'\x00\x02',1)
        # ghi vao D1014 gia tri 2
        #fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x03\xF6\x00',b'\x00\x02',1) 

        # ghi vao D2002 gia tri 0
        fins_instance.memory_area_write(FinsPLCMemoryAreas().DATA_MEMORY_WORD,b'\x07\xD2\x00',b'\x00\x00',1)            
        
        name_folder_ok = time_to_name()
        cv2.imwrite('G:/result/Cam2/OK/' + name_folder_ok  + '.jpg',img2_orgin)        
        
        img2_orgin = cv2.resize(img2_orgin,(640,480))
        imgbytes2 = cv2.imencode('.png',img2_orgin)[1].tobytes()
        window['image2'].update(data= imgbytes2)

        t2 = time.time() - t1
        print(t2) 


        print('---------------------------------------------')
        



def task_camera1_snap(model,size,conf):
    if event =='Snap1': 
        t1 = time.time()
        img1_orgin = camera1.GetImage().GetNPArray()                         # 0.0
        #img1_orgin = cv2.resize(img1_orgin,(640,480))
        #img1_orgin = Image.open(img1_orgin)
        #cv2.imshow('asd',img1_orgin)
        # name_folder_ok = time_to_name()
        # cv2.imwrite('G:/result/Cam1/test/' + name_folder_ok  + '.jpg',img1_orgin)
        img1_orgin = img1_orgin[50:530,70:710]
        img1_orgin = img1_orgin.copy()
        img1_orgin = cv2.cvtColor(img1_orgin, cv2.COLOR_BGR2RGB)
        result1 = model(img1_orgin,size= size,conf = conf)             # 0.015
        table1 = result1.pandas().xyxy[0]
        area_remove1 = []

        for item in range(len(table1.index)):
            width1 = table1['xmax'][item] - table1['xmin'][item]
            height1 = table1['ymax'][item] - table1['ymin'][item]
            area1 = width1*height1
            if table1['name'][item] == 'nut_me':
                if area1 < values['area_nutme1_a22']: 
                    table1.drop(item, axis=0, inplace=True)
                    area_remove1.append(item)

            elif table1['name'][item] == 'divat':
                if area1 < values['area_divat1_a22']: 
                    table1.drop(item, axis=0, inplace=True)
                    area_remove1.append(item)

            elif table1['name'][item] == 'me':
                if area1 < values['area_me1_a22']: 
                    table1.drop(item, axis=0, inplace=True)
                    area_remove1.append(item)

            elif table1['name'][item] == 'namchamcao':
                if height1 < values['y_namchamcao1_a22']: 
                    table1.drop(item, axis=0, inplace=True)
                    area_remove1.append(item)

            elif table1['name'][item] == 'tray_bac_truc':
                if area1 < values['area_traybactruc1_a22']: 
                    table1.drop(item, axis=0, inplace=True)
                    area_remove1.append(item)

            elif table1['name'][item] == 'di_vat_duoi':
                if area1 < values['area_divatduoi1_a22']: 
                    table1.drop(item, axis=0, inplace=True)
                    area_remove1.append(item)

            elif table1['name'][item] == 'kimcao':
                if height1 < values['ymin_kimnamcham1_a22']: 
                    table1.drop(item, axis=0, inplace=True)
                    area_remove1.append(item)
                elif height1 > values['ymax_kimnamcham1_a22']: 
                    table1.drop(item, axis=0, inplace=True)
                    area_remove1.append(item)
                print(height1)
        
        names1 = list(table1['name'])
        print(names1)

        show1 = np.squeeze(result1.render(area_remove1))
        show1 = cv2.resize(show1, (image_width_display,image_height_display), interpolation = cv2.INTER_AREA)

        len_ncc = 0
        len_kimcao = 0
        for find_name1 in names1:
            if find_name1 == 'namchamcao':
                len_ncc +=1

            if find_name1 == 'kimcao':
                len_kimcao += 1


        if 'kimnamcham' not in names1 or len_ncc !=2 or len_kimcao !=2 \
        or 'divat' in names1 or 'me' in names1 or 'nut_me' in names1 or 'nut' in names1 \
        or 'tray_bac_truc' in names1 or 'di_vat_duoi' in names1:
            print('NG')
            cv2.putText(show1, 'NG',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,0,255),5)
            window['result_cam1'].update(value= 'NG', text_color='red')
            name_folder_ng = time_to_name()
            cv2.imwrite('G:/result/Cam1/NG/' + name_folder_ng + '.jpg',img1_orgin)
            cv2.imwrite('G:/Windows/1/' + name_folder_ng + '.jpg',img1_orgin)

        else:
            print('OK')
            cv2.putText(show1, 'OK',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,255,0),5)
            window['result_cam1'].update(value= 'OK', text_color='green')
            name_folder_ok = time_to_name()
            cv2.imwrite('G:/result/Cam1/OK/' + name_folder_ok  + '.jpg',img1_orgin)
           
        imgbytes1 = cv2.imencode('.png',show1)[1].tobytes()
        window['image1'].update(data= imgbytes1)

        t2 = time.time() - t1
        print(t2) 
    
        print('---------------------------------------------')



def task_camera2_snap(model,size,conf):
    if event =='Snap2': 
        t3 = time.time()
        img2_orgin = camera2.GetImage().GetNPArray()

        result2 = model(img2_orgin,size= size,conf = conf) 

        table2 = result2.pandas().xyxy[0]

        area_remove2 = []
        for item in range(len(table2.index)):
            width2 = table2['xmax'][item] - table2['xmin'][item]
            height2 = table2['ymax'][item] - table2['ymin'][item]
            area2 = width2*height2
            if table2['name'][item] == 'nut_me':
                if area2 < values['area_nutme2_a22']: 
                    table2.drop(item, axis=0, inplace=True)
                    area_remove2.append(item)

            elif table2['name'][item] == 'divat':
                if area2 < values['area_divat2_a22']: 
                    table2.drop(item, axis=0, inplace=True)
                    area_remove2.append(item)

            elif table2['name'][item] == 'me':
                if area2 < values['area_me2_a22']: 
                    table2.drop(item, axis=0, inplace=True)
                    area_remove2.append(item)

        names2 = list(table2['name'])
        print(names2)

        save_memorys2 = []
        if 'namcham' not in names2 or 'divat' in names2 or 'me' in names2 or 'namchamcao' in names2 or 'nut_me' in names2 or 'nut' in names2:
            save_memorys2.append(1014)
        # thieu kimnamcham 1012 va bactruc 1010

        show2 = np.squeeze(result2.render(area_remove2))
        show2 = cv2.resize(show2, (image_width_display,image_height_display), interpolation = cv2.INTER_AREA)

        if 'namcham' not in names2 \
        or 'divat' in names2 or 'me' in names2 or 'namchamcao' in names2 or 'nut_me' in names2 or 'nut' in names2:
            print('NG')
            cv2.putText(show2, 'NG',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,0,255),5)
            window['result_cam2'].update(value= 'NG', text_color='red')  
            name_folder_ng = time_to_name()
            cv2.imwrite('G:/result/Cam2/NG/' + name_folder_ng + '.jpg',img2_orgin)   
            cv2.imwrite('G:/Windows/2/' + name_folder_ng + '.jpg',img2_orgin)     

        else:
            print('OK')
            cv2.putText(show2, 'OK',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,255,0),5)
            window['result_cam2'].update(value= 'OK', text_color='green')
            name_folder_ok = time_to_name()
            cv2.imwrite('G:/result/Cam2/OK/' + name_folder_ok + '.jpg',img2_orgin)


        imgbytes2 = cv2.imencode('.png',show2)[1].tobytes()
        window['image2'].update(data= imgbytes2)
                        
        t4 = time.time() - t3
        print(t4) 

        print('---------------------------------------------')



def make_window(theme):
    sg.theme(theme)

    #file_img = [("JPEG (*.jpg)",("*jpg","*.png"))]

    file_weights = [('Weights (*.pt)', ('*.pt'))]

    # menu = [['Application', ['Connect PLC','Interrupt Connect PLC','Exit']],
    #         ['Tool', ['Check Cam','Change Theme']],
    #         ['Help',['About']]]

    right_click_menu = [[], ['Exit','Administrator','Change Theme']]


    layout_main = [

        [
        sg.Text('CAM 2',justification='center' ,font= ('Helvetica',30),text_color='red',expand_x=True),
        sg.Text('CAM 1',justification='center' ,font= ('Helvetica',30),text_color='red',expand_x=True)],
        # sg.Frame('',[
        #     [sg.Text('CAM 2',justification='center' ,font= ('Helvetica',30),text_color='red',expand_x=True),
        #     sg.Text('CAM 1',justification='center' ,font= ('Helvetica',30),text_color='red',expand_x=True)],
        # ]),

        [

        # 2
        sg.Frame('',[
            #[sg.Image(filename='', size=(640,480),key='image1',background_color='black')],
            [sg.Image(filename='', size=(image_width_display,image_height_display),key='image2',background_color='black',expand_x=True, expand_y=True)],
            [sg.Frame('',
            [
                [sg.Text('',auto_size_text=True,font=('Helvetica',120), justification='center', key='result_cam2',expand_x=True, expand_y=True)],
                [sg.Text('',font=('Helvetica',30),justification='center', key='time_cam2',expand_x=True, expand_y=True)],
            ], vertical_alignment='top',size=(520,250),expand_x=True, expand_y=True),
            sg.Frame('',[
                #[sg.Text('')],
                [sg.Button('Webcam', size=(8,1),  font=('Helvetica',14),disabled=True,key= 'Webcam2',expand_x=True, expand_y=True,auto_size_button=True)],
                [sg.Text('',expand_x=True, expand_y=True)],
                [sg.Button('Stop', size=(8,1), font=('Helvetica',14),disabled=True  ,key='Stop2',expand_x=True, expand_y=True)],
                [sg.Text('',expand_x=True, expand_y=True)],
                #[sg.Button('Continue', size=(8,1),  font=('Helvetica',14),disabled=True ,key='Continue2')],
                #[sg.Text('')],
                [sg.Button('Snap', size=(8,1), font=('Helvetica',14),disabled=True  ,key='Snap2',expand_x=True, expand_y=True)],
                [sg.Text('',expand_x=True, expand_y=True)],
                [sg.Checkbox('Model',size=(6,1),font=('Helvetica',14), disabled=True, key='have_model2',expand_x=True, expand_y=True)]

                ],element_justification='center', vertical_alignment='top', relief= sg.RELIEF_FLAT,expand_x=True, expand_y=True),

            sg.Frame('',[   
                [sg.Button('Change', size=(8,1), font=('Helvetica',14), disabled= True, key= 'Change2',expand_x=True, expand_y=True)],
                [sg.Text('',expand_x=True, expand_y=True)],
                [sg.Button('Pic', size=(8,1), font=('Helvetica',14),disabled=True,key='Pic2',expand_x=True, expand_y=True)],
                [sg.Text('',expand_x=True, expand_y=True)],
                [sg.Button('Detect', size=(8,1), font=('Helvetica',14),disabled=True ,key= 'Detect2',expand_x=True, expand_y=True)],
                [sg.Text('',size=(4,2),expand_x=True, expand_y=True)],
                [sg.Text('',size=(4,1),expand_x=True, expand_y=True)],
                #[sg.Button('SaveData', size=(8,1), font=('Helvetica',14),disabled=True ,key= 'SaveData2_a22')],

                ],element_justification='center', vertical_alignment='top', relief= sg.RELIEF_FLAT,expand_x=True, expand_y=True),
            ]
        ], expand_x=True, expand_y= True),

        #1
        sg.Frame('',[
            #[sg.Image(filename='', size=(640,480),key='image1',background_color='black')],
            [sg.Image(filename='', size=(image_width_display,image_height_display),key='image1',background_color='black',expand_x=True, expand_y=True)],
            [sg.Frame('',
            [
                [sg.Text('',auto_size_text=True,font=('Helvetica',120), justification='center', key='result_cam1',expand_x=True, expand_y=True)],
                [sg.Text('',font=('Helvetica',30), justification='center', key='time_cam1',expand_x=True, expand_y=True)],
            ], vertical_alignment='top',size=(520,250),expand_x=True, expand_y=True),
            sg.Frame('',[
                #[sg.Text('')],
                [sg.Button('Webcam', size=(8,1),  font=('Helvetica',14),disabled=True ,key= 'Webcam1',expand_x=True, expand_y=True)],
                [sg.Text('',expand_x=True, expand_y=True)],
                [sg.Button('Stop', size=(8,1), font=('Helvetica',14),disabled=True ,key= 'Stop1',expand_x=True, expand_y=True)],
                [sg.Text('',expand_x=True, expand_y=True)],
                #[sg.Button('Continue', size=(8,1),  font=('Helvetica',14), disabled=True, key= 'Continue1')],
                #[sg.Text('')],
                [sg.Button('Snap', size=(8,1), font=('Helvetica',14),disabled=True ,key= 'Snap1',expand_x=True, expand_y=True)],
                [sg.Text('',expand_x=True, expand_y=True)],
                [sg.Checkbox('Model',size=(6,1),font=('Helvetica',14), disabled=True, key='have_model1',expand_x=True, expand_y=True)]
                #],element_justification='center',expand_x=True, vertical_alignment='top', relief= sg.RELIEF_FLAT),
                ],element_justification='center', vertical_alignment='top', relief= sg.RELIEF_FLAT,expand_x=True, expand_y=True),
                
            sg.Frame('',[   
                [sg.Button('Change', size=(8,1), font=('Helvetica',14), disabled= True, key= 'Change1',expand_x=True, expand_y=True)],
                [sg.Text('',expand_x=True, expand_y=True)],
                [sg.Button('Pic', size=(8,1), font=('Helvetica',14),disabled=True,key= 'Pic1',expand_x=True, expand_y=True)],
                [sg.Text('',expand_x=True, expand_y=True)],
                [sg.Button('Detect', size=(8,1), font=('Helvetica',14),disabled=True,key= 'Detect1',expand_x=True, expand_y=True)],
                [sg.Text('',expand_x=True, expand_y=True)],
                [sg.InputCombo(('A22','A19'),size=(1,200),font=('Helvetica',20),default_value=choose_model,key='change_model',enable_events=True,expand_x=True, expand_y=True)],
                # [sg.Text('',size=(14,2),expand_x=True, expand_y=True)],
                # [sg.Text('',size=(14,1),expand_x=True, expand_y=True)],
                #[sg.Button('SaveData', size=(8,1), font=('Helvetica',14),disabled=True,key= 'SaveData1_a22')],

                ],element_justification='center', vertical_alignment='top', relief= sg.RELIEF_FLAT,expand_x=True, expand_y=True),
            ],
                
        ],expand_x=True, expand_y=True),
    
    ]] 


    layout_parameter_model_A22 = [
        [sg.Text('CAM 2', size =(34,1),justification='center' ,font= ('Helvetica',30),text_color='red'),
         sg.Text('CAM 1', size =(34,1),justification='center' ,font= ('Helvetica',30),text_color='red')],
        # 2
        [
        sg.Frame('',[
            [sg.Frame('',
            [
                [sg.Text('Weights A22', size=(12,1), font=('Helvetica',15),text_color='yellow'), sg.Input(size=(52,1), font=('Helvetica',12), key='file_weights2_a22',readonly= True, text_color='navy',default_text=list_param_model2_a22[0],enable_events= True),
                sg.Frame('',[
                    [sg.FileBrowse(file_types= file_weights, size=(12,1), font=('Helvetica',10),key= 'file_browse2_a22',enable_events=True, disabled=True)]
                ], relief= sg.RELIEF_FLAT)],

                [sg.Text('Size', size=(12,1),font=('Helvetica',15), text_color='yellow'),sg.InputCombo((416,512,608,896,1024,1280,1408,1536),size=(56,20),font=('Helvetica',11),disabled=True,default_value=list_param_model2_a22[1],key='imgsz2_a22')],
                [sg.Text('Confidence',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,100),orientation='h',size=(52,20),font=('Helvetica',11),disabled=True,default_value=list_param_model2_a22[2], key= 'conf_thres2_a22')],
                [sg.Text('Nut me',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,20000),orientation='h',size=(52,20),font=('Helvetica',11),disabled=True,default_value=list_param_model2_a22[3], resolution=5, key= 'area_nutme2_a22')],
                [sg.Text('Di vat',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,20000),orientation='h',size=(52,20),font=('Helvetica',11),disabled=True,default_value=list_param_model2_a22[4], resolution=5, key= 'area_divat2_a22')],
                [sg.Text('Me',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,20000),orientation='h',size=(52,20),font=('Helvetica',11),disabled=True ,default_value=list_param_model2_a22[5], resolution=5, key= 'area_me2_a22')],
                [sg.Text(' ')],
                [sg.Text(' '*152), sg.Button('Save Data', size=(12,1),  font=('Helvetica',12),key='SaveData2_a22',enable_events=True)] 
            ]),
            ]
        ], expand_y= True),

        #1
        sg.Frame('',[
            [sg.Frame('',
            [
                [sg.Text('Weights A22', size=(12,1), font=('Helvetica',15),text_color='yellow'), sg.Input(size=(52,1), font=('Helvetica',12), key='file_weights1_a22',readonly= True, text_color='navy',default_text=list_param_model1_a22[0],enable_events= True),
                sg.Frame('',[
                    [sg.FileBrowse(file_types= file_weights, size=(12,1), font=('Helvetica',10),key= 'file_browse1_a22',enable_events=True,disabled=True )]
                ], relief= sg.RELIEF_FLAT)],

                [sg.Text('Size', size=(12,1),font=('Helvetica',15), text_color='yellow'),sg.InputCombo((416,512,608,896,1024,1280,1408,1536),size=(56,20),font=('Helvetica',11),disabled=True ,default_value=list_param_model1_a22[1],key='imgsz1_a22')],
                [sg.Text('Confidence',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,100),orientation='h',size=(52,20),font=('Helvetica',11),disabled=True  ,default_value=list_param_model1_a22[2], key= 'conf_thres1_a22')],
                [sg.Text('Nut me',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,20000),orientation='h',size=(52,20),font=('Helvetica',11), disabled=True ,default_value=list_param_model1_a22[3], resolution=5, key= 'area_nutme1_a22')],
                [sg.Text('Di vat',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,20000),orientation='h',size=(52,20),font=('Helvetica',11), disabled=True ,default_value=list_param_model1_a22[4], resolution=5, key= 'area_divat1_a22')],
                [sg.Text('Me',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,20000),orientation='h',size=(52,20),font=('Helvetica',11), disabled=True ,default_value=list_param_model1_a22[5], resolution=5, key= 'area_me1_a22')],
                [sg.Text('Nam cham cao',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,500),orientation='h',size=(52,20),font=('Helvetica',11), disabled=True ,default_value=list_param_model1_a22[6], resolution=1, key= 'y_namchamcao1_a22')],
                [sg.Text('Tray bac truc',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,20000),orientation='h',size=(52,20),font=('Helvetica',11), disabled=True ,default_value=list_param_model1_a22[7], resolution=5, key= 'area_traybactruc1_a22')],
                [sg.Text('Di vat duoi',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,20000),orientation='h',size=(52,20),font=('Helvetica',11), disabled=True ,default_value=list_param_model1_a22[8], resolution=5, key= 'area_divatduoi1_a22')],
                [sg.Text('Kim cao min',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,500),orientation='h',size=(52,20),font=('Helvetica',11), disabled=True ,default_value=list_param_model1_a22[9], resolution=1, key= 'ymin_kimnamcham1_a22')],
                [sg.Text('Kim cao max',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,500),orientation='h',size=(52,20),font=('Helvetica',11), disabled=True ,default_value=list_param_model1_a22[10], resolution=1, key= 'ymax_kimnamcham1_a22')],
                [sg.Text(' ')],
                [sg.Text(' '*152), sg.Button('Save Data', size=(12,1),  font=('Helvetica',12),key='SaveData1_a22',enable_events=True)] 
            ]),
            ]
        ], expand_y= True),
    
    ]] 


    layout_parameter_model_A19 = [
        [sg.Text('CAM 2', size =(34,1),justification='center' ,font= ('Helvetica',30),text_color='red'),
         sg.Text('CAM 1', size =(34,1),justification='center' ,font= ('Helvetica',30),text_color='red')],
        # 2
        [
        sg.Frame('',[
            [sg.Frame('',
            [

                [sg.Text('Weights A19', size=(12,1), font=('Helvetica',15),text_color='yellow'), sg.Input(size=(52,1), font=('Helvetica',12), key='file_weights2_a19',readonly= True, text_color='navy',default_text=list_param_model2_a19[0],enable_events= True),
                sg.Frame('',[
                    [sg.FileBrowse(file_types= file_weights, size=(12,1), font=('Helvetica',10),key= 'file_browse2_a19',enable_events=True, disabled=True)]
                ], relief= sg.RELIEF_FLAT)],
                [sg.Text('Size', size=(12,1),font=('Helvetica',15), text_color='yellow'),sg.InputCombo((416,512,608,896,1024,1280,1408,1536),size=(56,20),font=('Helvetica',11),disabled=True,default_value=list_param_model2_a19[1],key='imgsz2_a19')],
                [sg.Text('Confidence',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,100),orientation='h',size=(52,20),font=('Helvetica',11),disabled=True,default_value=list_param_model2_a19[2], key= 'conf_thres2_a19')],
                [sg.Text('Nut me',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,20000),orientation='h',size=(52,20),font=('Helvetica',11),disabled=True,default_value=list_param_model2_a19[3], resolution=5, key= 'area_nutme2_a19')],
                [sg.Text('Di vat',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,20000),orientation='h',size=(52,20),font=('Helvetica',11),disabled=True,default_value=list_param_model2_a19[4], resolution=5, key= 'area_divat2_a19')],
                [sg.Text('Me',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,20000),orientation='h',size=(52,20),font=('Helvetica',11),disabled=True ,default_value=list_param_model2_a19[5], resolution=5, key= 'area_me2_a19')],
                [sg.Text(' ')],
                [sg.Text(' '*152), sg.Button('Save Data', size=(12,1),  font=('Helvetica',12),key='SaveData2_a19',enable_events=True)] 
            ]),
            ]
        ], expand_y= True),

        #1
        sg.Frame('',[
            [sg.Frame('',
            [

                [sg.Text('Weights A19', size=(12,1), font=('Helvetica',15),text_color='yellow'), sg.Input(size=(52,1), font=('Helvetica',12), key='file_weights1_a19',readonly= True, text_color='navy',default_text=list_param_model1_a19[0],enable_events= True),
                sg.Frame('',[
                    [sg.FileBrowse(file_types= file_weights, size=(12,1), font=('Helvetica',10),key= 'file_browse1_a19',enable_events=True,disabled=True )]
                ], relief= sg.RELIEF_FLAT)],
                [sg.Text('Size', size=(12,1),font=('Helvetica',15), text_color='yellow'),sg.InputCombo((416,512,608,896,1024,1280,1408,1536),size=(56,20),font=('Helvetica',11),disabled=True ,default_value=list_param_model1_a19[1],key='imgsz1_a19')],
                [sg.Text('Confidence',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,100),orientation='h',size=(52,20),font=('Helvetica',11),disabled=True  ,default_value=list_param_model1_a19[2], key= 'conf_thres1_a19')],
                [sg.Text('Nut me',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,20000),orientation='h',size=(52,20),font=('Helvetica',11), disabled=True ,default_value=list_param_model1_a19[3], resolution=5, key= 'area_nutme1_a19')],
                [sg.Text('Di vat',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,20000),orientation='h',size=(52,20),font=('Helvetica',11), disabled=True ,default_value=list_param_model1_a19[4], resolution=5, key= 'area_divat1_a19')],
                [sg.Text('Me',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,20000),orientation='h',size=(52,20),font=('Helvetica',11), disabled=True ,default_value=list_param_model1_a19[5], resolution=5, key= 'area_me1_a19')],
                [sg.Text('Nam cham cao',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,500),orientation='h',size=(52,20),font=('Helvetica',11), disabled=True ,default_value=list_param_model1_a19[6], resolution=1, key= 'y_namchamcao1_a19')],
                [sg.Text('Tray bac truc',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,20000),orientation='h',size=(52,20),font=('Helvetica',11), disabled=True ,default_value=list_param_model1_a19[7], resolution=5, key= 'area_traybactruc1_a19')],
                [sg.Text('Di vat duoi',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,20000),orientation='h',size=(52,20),font=('Helvetica',11), disabled=True ,default_value=list_param_model1_a19[8], resolution=5, key= 'area_divatduoi1_a19')],
                [sg.Text('Kim cao min',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,500),orientation='h',size=(52,20),font=('Helvetica',11), disabled=True ,default_value=list_param_model1_a19[9], resolution=1, key= 'ymin_kimnamcham1_a19')],
                [sg.Text('Kim cao max',size=(12,1),font=('Helvetica',15), text_color='yellow'), sg.Slider(range=(1,500),orientation='h',size=(52,20),font=('Helvetica',11), disabled=True ,default_value=list_param_model1_a19[10], resolution=1, key= 'ymax_kimnamcham1_a19')],
                [sg.Text(' ')],
                [sg.Text(' '*152), sg.Button('Save Data', size=(12,1),  font=('Helvetica',12),key='SaveData1_a19',enable_events=True)] 
            ]),
            ]
        ], expand_y= True),
    
    ]] 


    layout_terminal = [[sg.Text("Anything printed will display here!")],
                      [sg.Multiline( font=('Helvetica',14), expand_x=True, expand_y=True, write_only=True, autoscroll=True, auto_refresh=True,reroute_stdout=True, reroute_stderr=True, echo_stdout_stderr=True)]
                      ]
    
    layout = [[sg.TabGroup([[  sg.Tab('Main', layout_main),
                               sg.Tab('Parameter Model A22', layout_parameter_model_A22),
                               sg.Tab('Parameter Model A19', layout_parameter_model_A19),
                               sg.Tab('Output', layout_terminal)]], expand_x=True, expand_y=True)
               ]]

    layout[-1].append(sg.Sizegrip())
    window = sg.Window('HuynhLeVu', layout, location=(0,0),right_click_menu=right_click_menu,resizable=True).Finalize()
    window.bind('<Configure>',"Configure")
    window.Maximize()

    return window

image_width_display = 760
image_height_display = 480

result_width_display = 570
# image_width_display - 190
result_height_display = 100 


file_name_img = [("Img(*.jpg,*.png)",("*jpg","*.png"))]

recording1 = False
recording2 = False 

error_cam1 = True
error_cam2 = True

choose_model = load_choose_model()


list_param_model1_a22 = load_param_model('static/param_model1_A22.txt')
list_param_model2_a22 = load_param_model('static/param_model2_A22.txt')
list_param_model1_a19 = load_param_model('static/param_model1_A19.txt')
list_param_model2_a19 = load_param_model('static/param_model2_A19.txt')


list_param_camera1 = load_param_camera1()
list_param_camera2 = load_param_camera2()

themes = load_theme()
theme = themes[0]
window = make_window(theme)

window['result_cam1'].update(value= 'Wait', text_color='yellow')
window['result_cam2'].update(value= 'Wait', text_color='yellow')




# connected = False
# while connected == False:
#     connected = connect_plc('192.168.250.1')
#     print('connecting ....')
#     #event, values = window.read(timeout=20)

# print("connected plc")   
connect_camera1 = False
connect_camera2 = False

try:
    camera1 = neoapi.Cam()
    camera1.Connect()

    if camera1.f.PixelFormat.GetEnumValueList().IsReadable('BGR8'):
        camera1.f.PixelFormat.SetString('BGR8')
    elif camera1.f.PixelFormat.GetEnumValueList().IsReadable('Mono8'):
        camera1.f.PixelFormat.SetString('Mono8')
    connect_camera1 = True

except (neoapi.NeoException, Exception) as exc:
    print('error 1: ', exc)
    window['result_cam1'].update(value= 'Error', text_color='red')



try:
    camera2 = neoapi.Cam()
    camera2.Connect()

    if camera2.f.PixelFormat.GetEnumValueList().IsReadable('BGR8'):
        camera2.f.PixelFormat.SetString('BGR8')
    elif camera2.f.PixelFormat.GetEnumValueList().IsReadable('Mono8'):
        camera2.f.PixelFormat.SetString('Mono8')
    connect_camera2 = True

except (neoapi.NeoException, Exception) as exc:
    print('error 2: ', exc)
    window['result_cam2'].update(value= 'Error', text_color='red')


if choose_model == 'A22':
    mypath1 = list_param_model1_a22[0]
    model1 = torch.hub.load('./levu','custom', path= mypath1, source='local',force_reload =False)
elif choose_model == 'A19':
    mypath1 = list_param_model1_a19[1]
    model1 = torch.hub.load('./levu','custom', path= mypath1, source='local',force_reload =False)

img1_test = os.path.join(os.getcwd(), 'img/imgtest.jpg')
result1 = model1(img1_test,416,0.25) 
print('model1 already')


if choose_model == 'A22':
    mypath2 = list_param_model2_a22[0]
    model2 = torch.hub.load('./levu','custom', path= mypath2, source='local',force_reload =False)
elif choose_model == 'A19':
    mypath2 = list_param_model2_a19[1]
    model2 = torch.hub.load('./levu','custom', path= mypath2, source='local',force_reload =False)


img2_test = os.path.join(os.getcwd(), 'img/imgtest.jpg')
result2 = model2(img2_test,416,0.25) 

print('model2 already')

if connect_camera1 == True:
    window['result_cam1'].update(value= 'Done', text_color='blue')
if connect_camera2 == True:
    window['result_cam2'].update(value= 'Done', text_color='blue')

#removefile()
try:
    while True:
        event, values = window.read(timeout=20)

        #print(cb_func1)
        #print(cb_func2)
        if values['change_model'] == 'A22':

            if event =='Exit' or event == sg.WINDOW_CLOSED :
                break

            if event == 'Configure':
                if window.TKroot.state() == 'zoomed':
                    #print(window['image1'].get_size()[0])
                    image_width_display = window['image1'].get_size()[0]
                    image_height_display = window['image1'].get_size()[1]
                    result_width_display = image_width_display - 190
                    result_height_display = 100 


            if event =='Administrator':
                login_password = 'vu123'  # helloworld
                password = sg.popup_get_text(
                    'Enter Password: ', password_char='*') 
                if password == login_password:
                    sg.popup_ok('Login Successed!!! ',text_color='green', font=('Helvetica',14))  

                    window['imgsz2_a22'].update(disabled= False)
                    window['imgsz1_a22'].update(disabled= False)
                    window['conf_thres2_a22'].update(disabled= False)
                    window['conf_thres1_a22'].update(disabled= False)
                    window['area_nutme2_a22'].update(disabled= False)
                    window['area_nutme1_a22'].update(disabled= False)
                    window['area_divat2_a22'].update(disabled= False)
                    window['area_divat1_a22'].update(disabled= False)
                    window['area_me2_a22'].update(disabled= False)
                    window['area_me1_a22'].update(disabled= False)
                    window['y_namchamcao1_a22'].update(disabled= False)
                    window['area_traybactruc1_a22'].update(disabled= False)
                    window['area_divatduoi1_a22'].update(disabled= False)
                    window['ymin_kimnamcham1_a22'].update(disabled= False)
                    window['ymax_kimnamcham1_a22'].update(disabled= False)

                    window['imgsz2_a19'].update(disabled= False)
                    window['imgsz1_a19'].update(disabled= False)
                    window['conf_thres2_a19'].update(disabled= False)
                    window['conf_thres1_a19'].update(disabled= False)
                    window['area_nutme2_a19'].update(disabled= False)
                    window['area_nutme1_a19'].update(disabled= False)
                    window['area_divat2_a19'].update(disabled= False)
                    window['area_divat1_a19'].update(disabled= False)
                    window['area_me2_a19'].update(disabled= False)
                    window['area_me1_a19'].update(disabled= False)
                    window['y_namchamcao1_a19'].update(disabled= False)
                    window['area_traybactruc1_a19'].update(disabled= False)
                    window['area_divatduoi1_a19'].update(disabled= False)
                    window['ymin_kimnamcham1_a19'].update(disabled= False)
                    window['ymax_kimnamcham1_a19'].update(disabled= False)

                    window['file_browse2_a22'].update(disabled= False,button_color='turquoise')
                    window['file_browse1_a22'].update(disabled= False,button_color='turquoise')

                    window['file_browse2_a19'].update(disabled= False,button_color='turquoise')
                    window['file_browse1_a19'].update(disabled= False,button_color='turquoise')

                    window['SaveData1_a22'].update(disabled= False,button_color='turquoise')
                    window['SaveData2_a22'].update(disabled= False,button_color='turquoise')

                    window['SaveData1_a19'].update(disabled= False,button_color='turquoise')
                    window['SaveData2_a19'].update(disabled= False,button_color='turquoise')

                    window['Webcam1'].update(disabled= False,button_color='turquoise')
                    window['Webcam2'].update(disabled= False,button_color='turquoise')
                    window['Stop1'].update(disabled= False,button_color='turquoise')
                    window['Stop2'].update(disabled= False,button_color='turquoise')
                    window['Pic1'].update(disabled= False,button_color='turquoise')
                    window['Pic2'].update(disabled= False,button_color='turquoise')
                    window['Snap1'].update(disabled= False,button_color='turquoise')
                    window['Snap2'].update(disabled= False,button_color='turquoise')
                    window['Change1'].update(button_color='turquoise')
                    window['Change2'].update(button_color='turquoise')
                    window['Detect1'].update(button_color='turquoise')
                    window['Detect2'].update(button_color='turquoise')

                    window['have_model1'].update(disabled=False)
                    window['have_model2'].update(disabled=False)


        
                else:
                    sg.popup_cancel('Wrong Password!!!',text_color='red', font=('Helvetica',14))

            if event == 'Change Theme':
                layout_theme = [
                    [sg.Listbox(values= sg.theme_list(), size = (30,20),auto_size_text=18,default_values='Dark',key='theme', enable_events=True)],
                    [
                        [sg.Button('Apply'),
                        sg.Button('Cancel')]
                    ]
                ] 
                window_theme = sg.Window('Change Theme', layout_theme, location=(50,50),keep_on_top=True).Finalize()
                window_theme.set_min_size((300,400))   

                while True:
                    event_theme, values_theme = window_theme.read(timeout=20)
                    if event_theme == sg.WIN_CLOSEG:
                        break

                    if event_theme == 'Apply':
                        theme_choose = values_theme['theme'][0]
                        if theme_choose == 'Default':
                            continue
                        window.close()
                        window = make_window(theme_choose)
                        save_theme(theme_choose)
                        #print(theme_choose)
                    if event_theme == 'Cancel':
                        answer = sg.popup_yes_no('Do you want to exit?')
                        if answer == 'Yes':
                            break
                        if answer == 'No':
                            continue
                window_theme.close()


            if event == 'file_browse1_a22': 
                window['file_weights1_a22'].update(value=values['file_browse1_a22'])
                if values['file_browse1_a22']:
                    window['Change1'].update(disabled=False)
            if event == 'file_browse1_a19': 
                window['file_weights1_a19'].update(value=values['file_browse1_a19'])
                if values['file_browse1_a19']:
                    window['Change1'].update(disabled=False)

            if event == 'file_browse2_a22':
                window['file_weights2_a22'].update(value=values['file_browse2_a22'])
                if values['file_browse2_a22']:
                    window['Change2'].update(disabled=False)

            if event == 'file_browse2_a19':
                window['file_weights2_a19'].update(value=values['file_browse2_a19'])
                if values['file_browse2_a19']:
                    window['Change2'].update(disabled=False)

    #change model 
            if event == 'change_model':
                if values['change_model'] == 'A22':
                    model1 = torch.hub.load('./levu','custom', path= list_param_model1_a22[0], source='local',force_reload =False)
                    model2 = torch.hub.load('./levu','custom', path= list_param_model2_a22[0], source='local',force_reload =False)
                    save_choose_model(values['change_model'])
                    window['result_cam1'].update(value='A22')
                    window['result_cam2'].update(value='A22')

                if values['change_model'] == 'A19':
                    model1 = torch.hub.load('./levu','custom', path= list_param_model1_a19[0], source='local',force_reload =False)
                    model2 = torch.hub.load('./levu','custom', path= list_param_model2_a19[0], source='local',force_reload =False)
                    save_choose_model(values['change_model'])
                    window['result_cam1'].update(value='A19')
                    window['result_cam2'].update(value='A19')


            if event == 'SaveData1_a22':
                save_param_model1_A22(values['file_weights1_a22'], values['imgsz1_a22'],values['conf_thres1_a22'],values['area_nutme1_a22'], values['area_divat1_a22'],values['area_me1_a22'],values['y_namchamcao1_a22'],values['area_traybactruc1_a22'],values['area_divatduoi1_a22'] ,values['ymin_kimnamcham1_a22'],values['ymax_kimnamcham1_a22'])
                sg.popup('Saved param model 1 successed',font=('Helvetica',15), text_color='green',keep_on_top= True)


            if event == 'SaveData2_a22':
                save_param_model2_A22(values['file_weights2_a22'],values['imgsz2_a22'],values['conf_thres2_a22'] ,values['area_nutme2_a22'], values['area_divat2_a22'],values['area_me2_a22'])
                sg.popup('Saved param model 2 successed',font=('Helvetica',15), text_color='green',keep_on_top= True)


            if event == 'SaveData1_a19':
                save_param_model1_A19(values['file_weights1_a19'], values['imgsz1_a19'],values['conf_thres1_a19'],values['area_nutme1_a19'], values['area_divat1_a19'],values['area_me1_a19'],values['y_namchamcao1_a19'],values['area_traybactruc1_a19'],values['area_divatduoi1_a19'] ,values['ymin_kimnamcham1_a19'],values['ymax_kimnamcham1_a19'])
                sg.popup('Saved param model 1 successed',font=('Helvetica',15), text_color='green',keep_on_top= True)


            if event == 'SaveData2_a19':
                save_param_model2_A19(values['file_weights2_a19'], values['imgsz2_a19'],values['conf_thres2_a19'] ,values['area_nutme2_a19'], values['area_divat2_a19'],values['area_me2_a19'])
                sg.popup('Saved param model 2 successed',font=('Helvetica',15), text_color='green',keep_on_top= True)


                

            task_camera1_snap(model=model1,size= values['imgsz1_a22'],conf= values['conf_thres1_a22']/100)
            task_camera2_snap(model=model2,size= values['imgsz2_a22'],conf= values['conf_thres2_a22']/100)

            #task_camera1(model=model1,size= values['imgsz1_a22'],conf= values['conf_thres1_a22']/100)
            #task_camera2(model=model2,size= values['imgsz2_a22'],conf= values['conf_thres2_a22']/100)




            #test_camera1(model=model1,size= values['imgsz1_a22'],conf= values['conf_thres1_a22']/100)
            #test_camera2()

            #task1(model1,size= values['imgsz1_a22'],conf= values['conf_thres1_a22']/100)
            #task2(model2,size= values['imgsz2_a22'],conf= values['conf_thres2_a22']/100) 

            #task1(model,size,conf)
            #task2(model,size,conf) 


            ### threading

            #task1 = threading.Thread(target=task_camera1, args=(model1, values['imgsz1_a22'], values['conf_thres1_a22']/100,))
            #task2 = threading.Thread(target=task_camera2, args=(model2, values['imgsz2_a22'], values['conf_thres2_a22']/100,))

            #task1.start()
            #task2.start()

            #task1.join()
            #task2.join()

            # menu



            if event == 'Webcam1':
                #cap1 = cv2.VideoCapture(0)
                recording1 = True


            elif event == 'Stop1':
                recording1 = False 
                imgbytes1 = np.zeros([100,100,3],dtype=np.uint8)
                imgbytes1 = cv2.resize(imgbytes1, (image_width_display,image_height_display), interpolation = cv2.INTER_AREA)
                imgbytes1 = cv2.imencode('.png',imgbytes1)[1].tobytes()
                window['image1'].update(data=imgbytes1)
                window['result_cam1'].update(value='')



            if event == 'Webcam2':
                #cap2 = cv2.VideoCapture(1)
                recording2 = True



            elif event == 'Stop2':
                recording2 = False 
                imgbytes2 = np.zeros([100,100,3],dtype=np.uint8)
                imgbytes2 = cv2.resize(imgbytes2, (image_width_display,image_height_display), interpolation = cv2.INTER_AREA)
                imgbytes2 = cv2.imencode('.png',imgbytes2)[1].tobytes()
                window['image2'].update(data=imgbytes2)
                window['result_cam2'].update(value='')


            if recording1:
                if values['have_model1'] == True:
                    img1_orgin = camera1.GetImage().GetNPArray()
                    img1_orgin = img1_orgin[50:530,70:710]
                    img1_orgin = img1_orgin.copy()
                    img1_orgin = cv2.cvtColor(img1_orgin, cv2.COLOR_BGR2RGB)                              
                    result1 = model1(img1_orgin,size= values['imgsz1_a22'],conf= values['conf_thres1_a22']/100)             
                    table1 = result1.pandas().xyxy[0]
                    area_remove1 = []

                    for item in range(len(table1.index)):
                        width1 = table1['xmax'][item] - table1['xmin'][item]
                        height1 = table1['ymax'][item] - table1['ymin'][item]
                        area1 = width1*height1
                        if table1['name'][item] == 'nut_me':
                            if area1 < values['area_nutme1_a22']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'divat':
                            if area1 < values['area_divat1_a22']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'me':
                            if area1 < values['area_me1_a22']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'namchamcao':
                            if height1 < values['y_namchamcao1_a22']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'tray_bac_truc':
                            if area1 < values['area_traybactruc1_a22']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'di_vat_duoi':
                            if area1 < values['area_divatduoi1_a22']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'kimcao':
                            if height1 < values['ymin_kimnamcham1_a22']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)
                            elif height1 > values['ymax_kimnamcham1_a22']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                    
                    names1 = list(table1['name'])
                    print(names1)

                    show1 = np.squeeze(result1.render(area_remove1))
                    show1 = cv2.resize(show1, (image_width_display,image_height_display), interpolation = cv2.INTER_AREA)

                    len_ncc = 0
                    len_kimcao = 0
                    for find_name1 in names1:
                        if find_name1 == 'namchamcao':
                            len_ncc +=1

                        if find_name1 == 'kimcao':
                            len_kimcao += 1


                    if 'kimnamcham' not in names1 or len_ncc !=2 or len_kimcao !=2 \
                    or 'divat' in names1 or 'me' in names1 or 'nut_me' in names1 or 'nut' in names1 \
                    or 'tray_bac_truc' in names1 or 'di_vat_duoi' in names1:
                        print('NG')
                        cv2.putText(show1, 'NG',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,0,255),5)
                        window['result_cam1'].update(value= 'NG', text_color='red')

                    else:
                        print('OK')
                        cv2.putText(show1, 'OK',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,255,0),5)
                        window['result_cam1'].update(value= 'OK', text_color='green')
                    
                    imgbytes1 = cv2.imencode('.png',show1)[1].tobytes()
                    window['image1'].update(data= imgbytes1)
                else:
                    img1_orgin = camera1.GetImage().GetNPArray()
                    img1_orgin = img1_orgin[50:530,70:710]
                    img1_orgin = img1_orgin.copy()
                    img1_orgin = cv2.cvtColor(img1_orgin, cv2.COLOR_BGR2RGB) 
                    img1_resize = cv2.resize(img1_orgin,(image_width_display,image_height_display))
                    if img1_orgin is not None:
                        show1 = img1_resize
                        imgbytes1 = cv2.imencode('.png',show1)[1].tobytes()
                        window['image1'].update(data=imgbytes1)
                        window['result_cam1'].update(value='')


            if recording2:
                if values['have_model2'] == True:
                    img2_orgin = camera2.GetImage().GetNPArray()
                    
                    result2 = model2(img2_orgin,size= values['imgsz2_a22'],conf= values['conf_thres2_a22']/100) 

                    table2 = result2.pandas().xyxy[0]

                    area_remove2 = []
                    for item in range(len(table2.index)):
                        width2 = table2['xmax'][item] - table2['xmin'][item]
                        height2 = table2['ymax'][item] - table2['ymin'][item]
                        area2 = width2*height2
                        if table2['name'][item] == 'nut_me':
                            if area2 < values['area_nutme2_a22']: 
                                table2.drop(item, axis=0, inplace=True)
                                area_remove2.append(item)

                        elif table2['name'][item] == 'divat':
                            if area2 < values['area_divat2_a22']: 
                                table2.drop(item, axis=0, inplace=True)
                                area_remove2.append(item)

                        elif table2['name'][item] == 'me':
                            if area2 < values['area_me2_a22']: 
                                table2.drop(item, axis=0, inplace=True)
                                area_remove2.append(item)

                    names2 = list(table2['name'])
                    print(names2)

                    show2 = np.squeeze(result2.render(area_remove2))
                    show2 = cv2.resize(show2, (image_width_display,image_height_display), interpolation = cv2.INTER_AREA)

                    if 'namcham' not in names2 \
                    or 'divat' in names2 or 'me' in names2 or 'namchamcao' in names2 or 'nut_me' in names2 or 'nut' in names2:
                        print('NG')
                        cv2.putText(show2, 'NG',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,0,255),5)
                        window['result_cam2'].update(value= 'NG', text_color='red')  

                    else:
                        print('OK')
                        cv2.putText(show2, 'OK',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,255,0),5)
                        window['result_cam2'].update(value= 'OK', text_color='green')


                    imgbytes2 = cv2.imencode('.png',show2)[1].tobytes()
                    window['image2'].update(data= imgbytes2)
                else:
                    img2_orgin = camera2.GetImage().GetNPArray()
                    img2_resize = cv2.resize(img2_orgin,(image_width_display,image_height_display))
                    if img2_orgin is not None:
                        show2 = img2_resize
                        imgbytes2 = cv2.imencode('.png',show2)[1].tobytes()
                        window['image2'].update(data=imgbytes2)
                        window['result_cam2'].update(value='')



            if event == 'Pic1':
                dir_img1 = sg.popup_get_file('Choose your image 1',file_types=file_name_img,keep_on_top= True)
                if dir_img1 not in ('',None):
                    pic1 = Image.open(dir_img1)
                    img1_resize = pic1.resize((image_width_display,image_height_display))
                    imgbytes1 = ImageTk.PhotoImage(img1_resize)
                    window['image1'].update(data= imgbytes1)
                    window['Detect1'].update(disabled= False)         

            if event == 'Pic2':
                dir_img2 = sg.popup_get_file('Choose your image 2',file_types=file_name_img,keep_on_top= True)
                if dir_img2 not in ('',None):
                    pic2 = Image.open(dir_img2)
                    img2_resize = pic2.resize((image_width_display,image_height_display))
                    imgbytes2 = ImageTk.PhotoImage(img2_resize)
                    window['image2'].update(data=imgbytes2)
                    window['Detect2'].update(disabled= False)


            if event == 'Change1':
                model1= torch.hub.load('./levu','custom',path=values['file_weights1_a22'],source='local',force_reload=False)
                window['result_cam1'].update(value='A22')

            if event == 'Change2':
                model2= torch.hub.load('./levu','custom',path=values['file_weights2_a22'],source='local',force_reload=False)
                window['result_cam2'].update(value='A22')

            if event == 'Detect1':
                print('CAM 1 DETECT')
                t1 = time.time()
                try:
                    result1 = model1(pic1,size= values['imgsz1_a22'],conf = values['conf_thres1_a22']/100)
                    t2 = time.time() - t1
                    print(t2) 

                    table1 = result1.pandas().xyxy[0]

                    area_remove1 = []
                    for item in range(len(table1.index)):
                        width1 = table1['xmax'][item] - table1['xmin'][item]
                        height1 = table1['ymax'][item] - table1['ymin'][item]
                        area1 = width1*height1

                        if table1['name'][item] == 'nut_me':
                            if area1 < values['area_nutme1_a22']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'divat': 
                            if area1 < values['area_divat1_a22']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'me':
                            if area1 < values['area_me1_a22']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'namchamcao':
                            if height1 < values['y_namchamcao1_a22']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'tray_bac_truc':
                            if area1 < values['area_traybactruc1_a22']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'di_vat_duoi':
                            if area1 < values['area_divatduoi1_a22']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'kimcao':
                            if height1 < values['ymin_kimnamcham1_a22']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)
                            elif height1 > values['ymax_kimnamcham1_a22']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                    names1 = list(table1['name'])

                    show1 = np.squeeze(result1.render(area_remove1))
                    show1 = cv2.resize(show1, (image_width_display,image_height_display), interpolation = cv2.INTER_AREA)

                    len_ncc = 0
                    for ncc in names1:
                        if ncc == 'namchamcao':
                            len_ncc +=1
                    
                    len_kimcao = 0
                    for kimcao in names1:
                        if kimcao == 'kimcao':
                            len_kimcao += 1

                    if 'kimnamcham' not in names1 or len_ncc !=2 or len_kimcao !=2 \
                    or 'divat' in names1 or 'me' in names1 or 'nut_me' in names1 or 'nut' in names1 \
                    or 'tray_bac_truc' in names1 or 'di_vat_duoi' in names1:
                        print('NG')
                        cv2.putText(show1, 'NG',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,0,255),5)
                        window['result_cam1'].update(value= 'NG', text_color='red')
                    else:
                        print('OK')
                        cv2.putText(show1, 'OK',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,255,0),5)
                        window['result_cam1'].update(value= 'OK', text_color='green')

                    
                    imgbytes1 = cv2.imencode('.png',show1)[1].tobytes()
                    window['image1'].update(data= imgbytes1)
                
                except:
                    sg.popup_annoying("Don't have image", font=('Helvetica',14),text_color='red')
                
                t2 = time.time() - t1
                print(t2)
                print('---------------------------------------------') 


                
            if event == 'Detect2':
                print('CAM 2 DETECT')
                t1 = time.time()
                try:
                    result2 = model2(dir_img2,size= values['imgsz2_a22'],conf = values['conf_thres2_a22']/100)
                    t2 = time.time() - t1
                    print(t2) 
                
                    table2 = result2.pandas().xyxy[0]

                    area_remove2 = []
                    for item in range(len(table2.index)):
                        width2 = table2['xmax'][item] - table2['xmin'][item]
                        height2 = table2['ymax'][item] - table2['ymin'][item]
                        area2 = width2*height2
                        if table2['name'][item] == 'nut_me':
                            if area2 < values['area_nutme2_a22']: 
                                table2.drop(item, axis=0, inplace=True)
                                area_remove2.append(item)
                        
                        elif table2['name'][item] == 'divat':
                            if area2 < values['area_divat2_a22']: 
                                table2.drop(item, axis=0, inplace=True)
                                area_remove2.append(item)

                        elif table2['name'][item] == 'me':
                            if area2 < values['area_me2_a22']: 
                                table2.drop(item, axis=0, inplace=True)
                                area_remove2.append(item)

                    names2 = list(table2['name'])

                    show2 = np.squeeze(result2.render(area_remove2))
                    show2 = cv2.resize(show2, (image_width_display,image_height_display), interpolation = cv2.INTER_AREA)

                    if 'namcham' not in names2 \
                    or 'divat' in names2 or 'me' in names2 or 'namchamcao' in names2 or 'nut_me' in names2 or 'nut' in names2:
                        print('NG')
                        cv2.putText(show2, 'NG',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,0,255),5)
                        window['result_cam2'].update(value= 'NG', text_color='red')       

                    else:
                        print('OK')
                        cv2.putText(show2, 'OK',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,255,0),5)
                        window['result_cam2'].update(value= 'OK', text_color='green')

                    imgbytes2 = cv2.imencode('.png',show2)[1].tobytes()
                    window['image2'].update(data= imgbytes2)
                except:
                    sg.popup_annoying("Don't have image", font=('Helvetica',14),text_color='red')

                t2 = time.time() - t1
                print(t2) 
                print('---------------------------------------------')
            

            #Save
            if event == 'save_param_camera1':
                #save_param_camera1(values['exposure_slider1'],values['gain_slider1'])
                save_param_camera1(values['exposure_slider1'],values['gain_slider1'],values['red_slider1'],values['green_slider1'],values['blue_slider1'])
                sg.popup('Saved successed',font=('Helvetica',15), text_color='green',keep_on_top= True)


            #Save
            if event == 'save_param_camera2':
                save_param_camera2(values['exposure_slider2'],values['gain_slider2'])
                sg.popup('Saved successed',font=('Helvetica',15), text_color='green',keep_on_top= True)



        if values['change_model'] == 'A19':

            if event =='Exit' or event == sg.WINDOW_CLOSED :
                break

            if event == 'Configure':
                if window.TKroot.state() == 'zoomed':
                    #print(window['image1'].get_size()[0])
                    image_width_display = window['image1'].get_size()[0]
                    image_height_display = window['image1'].get_size()[1]
                    result_width_display = image_width_display - 190
                    result_height_display = 100 


            if event =='Administrator':
                login_password = 'vu123'  # helloworld
                password = sg.popup_get_text(
                    'Enter Password: ', password_char='*') 
                if password == login_password:
                    sg.popup_ok('Login Successed!!! ',text_color='green', font=('Helvetica',14))  

                    window['imgsz2_a22'].update(disabled= False)
                    window['imgsz1_a22'].update(disabled= False)
                    window['conf_thres2_a22'].update(disabled= False)
                    window['conf_thres1_a22'].update(disabled= False)
                    window['area_nutme2_a22'].update(disabled= False)
                    window['area_nutme1_a22'].update(disabled= False)
                    window['area_divat2_a22'].update(disabled= False)
                    window['area_divat1_a22'].update(disabled= False)
                    window['area_me2_a22'].update(disabled= False)
                    window['area_me1_a22'].update(disabled= False)
                    window['y_namchamcao1_a22'].update(disabled= False)
                    window['area_traybactruc1_a22'].update(disabled= False)
                    window['area_divatduoi1_a22'].update(disabled= False)
                    window['ymin_kimnamcham1_a22'].update(disabled= False)
                    window['ymax_kimnamcham1_a22'].update(disabled= False)

                    window['imgsz2_a19'].update(disabled= False)
                    window['imgsz1_a19'].update(disabled= False)
                    window['conf_thres2_a19'].update(disabled= False)
                    window['conf_thres1_a19'].update(disabled= False)
                    window['area_nutme2_a19'].update(disabled= False)
                    window['area_nutme1_a19'].update(disabled= False)
                    window['area_divat2_a19'].update(disabled= False)
                    window['area_divat1_a19'].update(disabled= False)
                    window['area_me2_a19'].update(disabled= False)
                    window['area_me1_a19'].update(disabled= False)
                    window['y_namchamcao1_a19'].update(disabled= False)
                    window['area_traybactruc1_a19'].update(disabled= False)
                    window['area_divatduoi1_a19'].update(disabled= False)
                    window['ymin_kimnamcham1_a19'].update(disabled= False)
                    window['ymax_kimnamcham1_a19'].update(disabled= False)

                    window['file_browse2_a22'].update(disabled= False,button_color='turquoise')
                    window['file_browse1_a22'].update(disabled= False,button_color='turquoise')

                    window['file_browse2_a19'].update(disabled= False,button_color='turquoise')
                    window['file_browse1_a19'].update(disabled= False,button_color='turquoise')

                    window['SaveData1_a22'].update(disabled= False,button_color='turquoise')
                    window['SaveData2_a22'].update(disabled= False,button_color='turquoise')

                    window['SaveData1_a19'].update(disabled= False,button_color='turquoise')
                    window['SaveData2_a19'].update(disabled= False,button_color='turquoise')

                    window['Webcam1'].update(disabled= False,button_color='turquoise')
                    window['Webcam2'].update(disabled= False,button_color='turquoise')
                    window['Stop1'].update(disabled= False,button_color='turquoise')
                    window['Stop2'].update(disabled= False,button_color='turquoise')
                    window['Pic1'].update(disabled= False,button_color='turquoise')
                    window['Pic2'].update(disabled= False,button_color='turquoise')
                    window['Snap1'].update(disabled= False,button_color='turquoise')
                    window['Snap2'].update(disabled= False,button_color='turquoise')
                    window['Change1'].update(button_color='turquoise')
                    window['Change2'].update(button_color='turquoise')
                    window['Detect1'].update(button_color='turquoise')
                    window['Detect2'].update(button_color='turquoise')

                    window['have_model1'].update(disabled=False)

                    window['have_model2'].update(disabled=False)

  
                else:
                    sg.popup_cancel('Wrong Password!!!',text_color='red', font=('Helvetica',14))

            if event == 'Change Theme':
                layout_theme = [
                    [sg.Listbox(values= sg.theme_list(), size = (30,20),auto_size_text=18,default_values='Dark',key='theme', enable_events=True)],
                    [
                        [sg.Button('Apply'),
                        sg.Button('Cancel')]
                    ]
                ] 
                window_theme = sg.Window('Change Theme', layout_theme, location=(50,50),keep_on_top=True).Finalize()
                window_theme.set_min_size((300,400))   

                while True:
                    event_theme, values_theme = window_theme.read(timeout=20)
                    if event_theme == sg.WIN_CLOSEG:
                        break

                    if event_theme == 'Apply':
                        theme_choose = values_theme['theme'][0]
                        if theme_choose == 'Default':
                            continue
                        window.close()
                        window = make_window(theme_choose)
                        save_theme(theme_choose)
                        #print(theme_choose)
                    if event_theme == 'Cancel':
                        answer = sg.popup_yes_no('Do you want to exit?')
                        if answer == 'Yes':
                            break
                        if answer == 'No':
                            continue
                window_theme.close()


            if event == 'file_browse1_a22': 
                window['file_weights1_a22'].update(value=values['file_browse1_a22'])
                if values['file_browse1_a22']:
                    window['Change1'].update(disabled=False)
            if event == 'file_browse1_a19': 
                window['file_weights1_a19'].update(value=values['file_browse1_a19'])
                if values['file_browse1_a19']:
                    window['Change1'].update(disabled=False)

            if event == 'file_browse2_a22':
                window['file_weights2_a22'].update(value=values['file_browse2_a22'])
                if values['file_browse2_a22']:
                    window['Change2'].update(disabled=False)

            if event == 'file_browse2_a19':
                window['file_weights2_a19'].update(value=values['file_browse2_a19'])
                if values['file_browse2_a19']:
                    window['Change2'].update(disabled=False)

    #change model 
            if event == 'change_model':
                if values['change_model'] == 'A22':
                    model1 = torch.hub.load('./levu','custom', path= list_param_model1_a22[0], source='local',force_reload =False)
                    model2 = torch.hub.load('./levu','custom', path= list_param_model2_a22[0], source='local',force_reload =False)
                    save_choose_model(values['change_model'])
                    window['result_cam1'].update(value='A22')
                    window['result_cam2'].update(value='A22')

                if values['change_model'] == 'A19':
                    model1 = torch.hub.load('./levu','custom', path= list_param_model1_a19[0], source='local',force_reload =False)
                    model2 = torch.hub.load('./levu','custom', path= list_param_model2_a19[0], source='local',force_reload =False)
                    save_choose_model(values['change_model'])
                    window['result_cam1'].update(value='A19')
                    window['result_cam2'].update(value='A19')


            if event == 'SaveData1_a22':
                save_param_model1_A22(values['file_weights1_a22'], values['imgsz1_a22'],values['conf_thres1_a22'],values['area_nutme1_a22'], values['area_divat1_a22'],values['area_me1_a22'],values['y_namchamcao1_a22'],values['area_traybactruc1_a22'],values['area_divatduoi1_a22'] ,values['ymin_kimnamcham1_a22'],values['ymax_kimnamcham1_a22'])
                sg.popup('Saved param model 1 successed',font=('Helvetica',15), text_color='green',keep_on_top= True)


            if event == 'SaveData2_a22':
                save_param_model2_A22(values['file_weights2_a22'],values['imgsz2_a22'],values['conf_thres2_a22'] ,values['area_nutme2_a22'], values['area_divat2_a22'],values['area_me2_a22'])
                sg.popup('Saved param model 2 successed',font=('Helvetica',15), text_color='green',keep_on_top= True)


            if event == 'SaveData1_a19':
                save_param_model1_A19(values['file_weights1_a19'], values['imgsz1_a19'],values['conf_thres1_a19'],values['area_nutme1_a19'], values['area_divat1_a19'],values['area_me1_a19'],values['y_namchamcao1_a19'],values['area_traybactruc1_a19'],values['area_divatduoi1_a19'] ,values['ymin_kimnamcham1_a19'],values['ymax_kimnamcham1_a19'])
                sg.popup('Saved param model 1 successed',font=('Helvetica',15), text_color='green',keep_on_top= True)


            if event == 'SaveData2_a19':
                save_param_model2_A19(values['file_weights2_a19'], values['imgsz2_a19'],values['conf_thres2_a19'] ,values['area_nutme2_a19'], values['area_divat2_a19'],values['area_me2_a19'])
                sg.popup('Saved param model 2 successed',font=('Helvetica',15), text_color='green',keep_on_top= True)






            task_camera1_snap(model=model1,size= values['imgsz1_a19'],conf= values['conf_thres1_a19']/100)
            task_camera2_snap(model=model2,size= values['imgsz2_a19'],conf= values['conf_thres2_a19']/100)


            # menu

            if event == 'Webcam1':
                #cap1 = cv2.VideoCapture(0)
                recording1 = True


            elif event == 'Stop1':
                recording1 = False 
                imgbytes1 = np.zeros([100,100,3],dtype=np.uint8)
                imgbytes1 = cv2.resize(imgbytes1, (image_width_display,image_height_display), interpolation = cv2.INTER_AREA)
                imgbytes1 = cv2.imencode('.png',imgbytes1)[1].tobytes()
                window['image1'].update(data=imgbytes1)
                window['result_cam1'].update(value='')



            if event == 'Webcam2':
                #cap2 = cv2.VideoCapture(1)
                recording2 = True



            elif event == 'Stop2':
                recording2 = False 
                imgbytes2 = np.zeros([100,100,3],dtype=np.uint8)
                imgbytes2 = cv2.resize(imgbytes2, (image_width_display,image_height_display), interpolation = cv2.INTER_AREA)
                imgbytes2 = cv2.imencode('.png',imgbytes2)[1].tobytes()
                window['image2'].update(data=imgbytes2)
                window['result_cam2'].update(value='')


            if recording1:
                if values['have_model1'] == True:
                    img1_orgin = camera1.GetImage().GetNPArray()
                    img1_orgin = img1_orgin[50:530,70:710]
                    img1_orgin = img1_orgin.copy()
                    img1_orgin = cv2.cvtColor(img1_orgin, cv2.COLOR_BGR2RGB)                              
                    result1 = model1(img1_orgin,size= values['imgsz1_a19'],conf= values['conf_thres1_a19']/100)             
                    table1 = result1.pandas().xyxy[0]
                    area_remove1 = []

                    for item in range(len(table1.index)):
                        width1 = table1['xmax'][item] - table1['xmin'][item]
                        height1 = table1['ymax'][item] - table1['ymin'][item]
                        area1 = width1*height1
                        if table1['name'][item] == 'nut_me':
                            if area1 < values['area_nutme1_a19']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'divat':
                            if area1 < values['area_divat1_a19']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'me':
                            if area1 < values['area_me1_a19']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'namchamcao':
                            if height1 < values['y_namchamcao1_a19']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'tray_bac_truc':
                            if area1 < values['area_traybactruc1_a19']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'di_vat_duoi':
                            if area1 < values['area_divatduoi1_a19']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'kimcao':
                            if height1 < values['ymin_kimnamcham1_a19']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)
                            elif height1 > values['ymax_kimnamcham1_a19']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                    
                    names1 = list(table1['name'])
                    print(names1)

                    show1 = np.squeeze(result1.render(area_remove1))
                    show1 = cv2.resize(show1, (image_width_display,image_height_display), interpolation = cv2.INTER_AREA)

                    len_ncc = 0
                    len_kimcao = 0
                    for find_name1 in names1:
                        if find_name1 == 'namchamcao':
                            len_ncc +=1

                        if find_name1 == 'kimcao':
                            len_kimcao += 1


                    if 'kimnamcham' not in names1 or len_ncc !=2 or len_kimcao !=2 \
                    or 'divat' in names1 or 'me' in names1 or 'nut_me' in names1 or 'nut' in names1 \
                    or 'tray_bac_truc' in names1 or 'di_vat_duoi' in names1:
                        print('NG')
                        cv2.putText(show1, 'NG',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,0,255),5)
                        window['result_cam1'].update(value= 'NG', text_color='red')

                    else:
                        print('OK')
                        cv2.putText(show1, 'OK',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,255,0),5)
                        window['result_cam1'].update(value= 'OK', text_color='green')
                    
                    imgbytes1 = cv2.imencode('.png',show1)[1].tobytes()
                    window['image1'].update(data= imgbytes1)
                else:
                    img1_orgin = camera1.GetImage().GetNPArray()
                    img1_orgin = img1_orgin[50:530,70:710]
                    img1_orgin = img1_orgin.copy()
                    img1_orgin = cv2.cvtColor(img1_orgin, cv2.COLOR_BGR2RGB) 
                    img1_resize = cv2.resize(img1_orgin,(image_width_display,image_height_display))
                    if img1_orgin is not None:
                        show1 = img1_resize
                        imgbytes1 = cv2.imencode('.png',show1)[1].tobytes()
                        window['image1'].update(data=imgbytes1)
                        window['result_cam1'].update(value='')


            if recording2:
                if values['have_model2'] == True:
                    img2_orgin = camera2.GetImage().GetNPArray()
                    
                    result2 = model2(img2_orgin,size= values['imgsz2_a19'],conf= values['conf_thres2_a19']/100) 

                    table2 = result2.pandas().xyxy[0]

                    area_remove2 = []
                    for item in range(len(table2.index)):
                        width2 = table2['xmax'][item] - table2['xmin'][item]
                        height2 = table2['ymax'][item] - table2['ymin'][item]
                        area2 = width2*height2
                        if table2['name'][item] == 'nut_me':
                            if area2 < values['area_nutme2_a19']: 
                                table2.drop(item, axis=0, inplace=True)
                                area_remove2.append(item)

                        elif table2['name'][item] == 'divat':
                            if area2 < values['area_divat2_a19']: 
                                table2.drop(item, axis=0, inplace=True)
                                area_remove2.append(item)

                        elif table2['name'][item] == 'me':
                            if area2 < values['area_me2_a19']: 
                                table2.drop(item, axis=0, inplace=True)
                                area_remove2.append(item)

                    names2 = list(table2['name'])
                    print(names2)

                    show2 = np.squeeze(result2.render(area_remove2))
                    show2 = cv2.resize(show2, (image_width_display,image_height_display), interpolation = cv2.INTER_AREA)

                    if 'namcham' not in names2 \
                    or 'divat' in names2 or 'me' in names2 or 'namchamcao' in names2 or 'nut_me' in names2 or 'nut' in names2:
                        print('NG')
                        cv2.putText(show2, 'NG',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,0,255),5)
                        window['result_cam2'].update(value= 'NG', text_color='red')  

                    else:
                        print('OK')
                        cv2.putText(show2, 'OK',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,255,0),5)
                        window['result_cam2'].update(value= 'OK', text_color='green')


                    imgbytes2 = cv2.imencode('.png',show2)[1].tobytes()
                    window['image2'].update(data= imgbytes2)
                else:
                    img2_orgin = camera2.GetImage().GetNPArray()
                    img2_resize = cv2.resize(img2_orgin,(image_width_display,image_height_display))
                    if img2_orgin is not None:
                        show2 = img2_resize
                        imgbytes2 = cv2.imencode('.png',show2)[1].tobytes()
                        window['image2'].update(data=imgbytes2)
                        window['result_cam2'].update(value='')




            if event == 'Pic1':
                dir_img1 = sg.popup_get_file('Choose your image 1',file_types=file_name_img,keep_on_top= True)
                if dir_img1 not in ('',None):
                    pic1 = Image.open(dir_img1)
                    img1_resize = pic1.resize((image_width_display,image_height_display))
                    imgbytes1 = ImageTk.PhotoImage(img1_resize)
                    window['image1'].update(data= imgbytes1)
                    window['Detect1'].update(disabled= False)         

            if event == 'Pic2':
                dir_img2 = sg.popup_get_file('Choose your image 2',file_types=file_name_img,keep_on_top= True)
                if dir_img2 not in ('',None):
                    pic2 = Image.open(dir_img2)
                    img2_resize = pic2.resize((image_width_display,image_height_display))
                    imgbytes2 = ImageTk.PhotoImage(img2_resize)
                    window['image2'].update(data=imgbytes2)
                    window['Detect2'].update(disabled= False)


            if event == 'Change1':
                model1= torch.hub.load('./levu','custom',path=values['file_weights1_a19'],source='local',force_reload=False)
                window['result_cam1'].update(value='A19') 
                #window['Detect1'].update(disabled= False)

            if event == 'Change2':
                model2 = torch.hub.load('./levu','custom',path=values['file_weights2_a19'],source='local',force_reload=False)
                window['result_cam2'].update(value='A19')


            if event == 'Detect1':
                print('CAM 1 DETECT')
                t1 = time.time()
                try:
                    result1 = model1(pic1,size= values['imgsz1_a19'],conf = values['conf_thres1_a19']/100)
                    t2 = time.time() - t1
                    print(t2) 

                    table1 = result1.pandas().xyxy[0]

                    area_remove1 = []
                    for item in range(len(table1.index)):
                        width1 = table1['xmax'][item] - table1['xmin'][item]
                        height1 = table1['ymax'][item] - table1['ymin'][item]
                        area1 = width1*height1

                        if table1['name'][item] == 'nut_me':
                            if area1 < values['area_nutme1_a19']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'divat': 
                            if area1 < values['area_divat1_a19']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'me':
                            if area1 < values['area_me1_a19']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'namchamcao':
                            if height1 < values['y_namchamcao1_a19']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'tray_bac_truc':
                            if area1 < values['area_traybactruc1_a19']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'di_vat_duoi':
                            if area1 < values['area_divatduoi1_a19']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                        elif table1['name'][item] == 'kimcao':
                            if height1 < values['ymin_kimnamcham1_a19']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)
                            elif height1 > values['ymax_kimnamcham1_a19']: 
                                table1.drop(item, axis=0, inplace=True)
                                area_remove1.append(item)

                    names1 = list(table1['name'])

                    show1 = np.squeeze(result1.render(area_remove1))
                    show1 = cv2.resize(show1, (image_width_display,image_height_display), interpolation = cv2.INTER_AREA)

                    len_ncc = 0
                    for ncc in names1:
                        if ncc == 'namchamcao':
                            len_ncc +=1
                    
                    len_kimcao = 0
                    for kimcao in names1:
                        if kimcao == 'kimcao':
                            len_kimcao += 1

                    if 'kimnamcham' not in names1 or len_ncc !=2 or len_kimcao !=2 \
                    or 'divat' in names1 or 'me' in names1 or 'nut_me' in names1 or 'nut' in names1 \
                    or 'tray_bac_truc' in names1 or 'di_vat_duoi' in names1:
                        print('NG')
                        cv2.putText(show1, 'NG',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,0,255),5)
                        window['result_cam1'].update(value= 'NG', text_color='red')
                    else:
                        print('OK')
                        cv2.putText(show1, 'OK',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,255,0),5)
                        window['result_cam1'].update(value= 'OK', text_color='green')

                    
                    imgbytes1 = cv2.imencode('.png',show1)[1].tobytes()
                    window['image1'].update(data= imgbytes1)
                
                except:
                    sg.popup_annoying("Don't have image", font=('Helvetica',14),text_color='red')
                
                t2 = time.time() - t1
                print(t2)
                print('---------------------------------------------') 


                
            if event == 'Detect2':
                print('CAM 2 DETECT')
                t1 = time.time()
                try:
                    result2 = model2(dir_img2,size= values['imgsz2_a19'],conf = values['conf_thres2_a19']/100)
                    t2 = time.time() - t1
                    print(t2) 
                
                    table2 = result2.pandas().xyxy[0]

                    area_remove2 = []
                    for item in range(len(table2.index)):
                        width2 = table2['xmax'][item] - table2['xmin'][item]
                        height2 = table2['ymax'][item] - table2['ymin'][item]
                        area2 = width2*height2
                        if table2['name'][item] == 'nut_me':
                            if area2 < values['area_nutme2_a19']: 
                                table2.drop(item, axis=0, inplace=True)
                                area_remove2.append(item)
                        
                        elif table2['name'][item] == 'divat':
                            if area2 < values['area_divat2_a19']: 
                                table2.drop(item, axis=0, inplace=True)
                                area_remove2.append(item)

                        elif table2['name'][item] == 'me':
                            if area2 < values['area_me2_a19']: 
                                table2.drop(item, axis=0, inplace=True)
                                area_remove2.append(item)

                    names2 = list(table2['name'])

                    show2 = np.squeeze(result2.render(area_remove2))
                    show2 = cv2.resize(show2, (image_width_display,image_height_display), interpolation = cv2.INTER_AREA)

                    if 'namcham' not in names2 \
                    or 'divat' in names2 or 'me' in names2 or 'namchamcao' in names2 or 'nut_me' in names2 or 'nut' in names2:
                        print('NG')
                        cv2.putText(show2, 'NG',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,0,255),5)
                        window['result_cam2'].update(value= 'NG', text_color='red')       

                    else:
                        print('OK')
                        cv2.putText(show2, 'OK',(result_width_display,result_height_display),cv2.FONT_HERSHEY_COMPLEX, 4,(0,255,0),5)
                        window['result_cam2'].update(value= 'OK', text_color='green')

                    imgbytes2 = cv2.imencode('.png',show2)[1].tobytes()
                    window['image2'].update(data= imgbytes2)
                except:
                    sg.popup_annoying("Don't have image", font=('Helvetica',14),text_color='red')

                t2 = time.time() - t1
                print(t2) 
                print('---------------------------------------------')
            


    window.close() 

except Exception as e:
    traceback.print_exc()
    str_error = str(e)
    sg.popup(str_error,font=('Helvetica',15), text_color='red',keep_on_top= True)

#pyinstaller --onefile app.py yolov5/hubconf.py yolov5/models/common.py yolov5/models/experimental.py yolov5/models/yolo.py yolov5/utils/augmentations.py yolov5/utils/autoanchor.py yolov5/utils/datasets.py yolov5/utils/downloads.py yolov5/utils/general.py yolov5/utils/metrics.py yolov5/utils/plots.py yolov5/utils/torch_utils.py
#pyinstaller --onedir --windowed app.py yolov5/hubconf.py yolov5/models/common.py yolov5/models/experimental.py yolov5/models/yolo.py yolov5/utils/augmentations.py yolov5/utils/autoanchor.py yolov5/utils/datasets.py yolov5/utils/downloads.py yolov5/utils/general.py yolov5/utils/metrics.py yolov5/utils/plots.py yolov5/utils/torch_utils.py                       