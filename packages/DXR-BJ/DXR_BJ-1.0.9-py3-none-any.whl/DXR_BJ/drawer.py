#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/07/17
# @Author  : zx
# @File    : Drawer.py
# @Version : 1.0.9


import copy
import math
import os
import traceback  ## log

import cv2
import freetype  ## Freetypechinese
import numpy as np

###全局变量
Version_num = '1.0.9'  ###版本号
py_path = os.path.dirname(os.path.abspath(__file__))  ##字体路径

## 中英对照表
alg_name = {
    "smoke": "烟雾",
    "fire": "火焰",
    "person": "行人",
    "car": "车",
    "IRPerson": "夜视行人",
    "open": "开启",
    "cover": "关闭",
    "close": "关闭",
    "fire hydrant": "消防栓",
    "bol": "扫帚",
    "axe": "消防斧",
    "exting": "灭火器",
    "shovel": "消防铲",
    "sandbox": "砂箱",
    "firebucket": "消防桶",
    "left": "左",
    "up": "上",
    "down": "下",
    "right": "右",
    "ok": "中",
    "Warning": "警告",
    "Normal": "正常",
    'manhole_cover': '井盖',
    "Pothole": "坑洼",
    "LCD": "液晶屏",
    "button": "指示灯",
    "pointer_watch": "指针表",
    "switch": "开关",
    "light": "指示灯",
    "drip": "滴漏区域",
    "hat": "戴帽",
    "no_hat": "未戴帽",
    "animal": "动物",
    "face": "人脸",
    "lpr": "车牌",
    "box":"箱子",
    "monkey": "猴子",
}

##发布 标记类把下面代码注释掉打开logger打印代码
# from common.utils.loginfo import logger


class logger():
    def info(message):
        print(message)
        return


### 定义框颜色类，包含20个颜色
class Colors:
    def __init__(self):
        hexs = ('FF3838', 'FF9D97',  ##红色 0 1
                'FF701F', 'FFB21D',  ##橙色 2 3
                'CFD231', '48F90A', '92CC17', '3DDB86', '1A9334',  ##绿色 4 -8
                '00D4BB', '2C99A8', '00C2FF', '344593', '6473FF', '0018EC',  ##蓝色 9-14
                '8438FF', '520085', 'CB38FF',  ##紫色 15-17
                'FF95C8', 'FF37C7')  ##粉色18 -19
        self.palette = [self.hex2rgb(f'#{c}') for c in hexs]
        self.n = len(self.palette)

    def __call__(self, i, bgr=False):
        c = self.palette[int(i) % self.n]
        return (c[2], c[1], c[0]) if bgr else c

    @staticmethod
    def hex2rgb(h):  # rgb order (PIL)
        return tuple(int(h[1 + i:1 + i + 2], 16) for i in (0, 2, 4))


### freetype-py标记类
class FreetypePy():
    def __init__(self, import_path="common/dependency"):
        self.import_path = import_path
        self.font_path = self.import_path + '/simsun.ttc'
        self.size = 64
        self._face = freetype.Face(self.font_path)
        self.imgwidth = 1920
        self.imgheight = 1080
        self.text_size = 20
        self.textcolor = (0, 255, 0)
        self.rectcolor = (0, 255, 0)
        self.background = (255, 255, 255)
        self.lw = 3 or max(round(sum((self.imgheight, self.imgwidth, 3)) / 2 * 0.003), 2)  # line width
        self.flag_rect = True
        return

    ## 图像 标签 位置 框颜色  标签颜色 是否车牌 是否要标记矩形框
    def DrawChinesename(self, outimg, label, position, rectcolor, labelcolor, flag_lpr=False, flag_rect=True):
        self.textcolor = labelcolor
        self.rectcolor = rectcolor
        self.flag_rect = flag_rect
        outimg = self.draw_text(outimg, position, label, self.text_size, labelcolor)  # 在图像上添加文本

        return outimg

    def draw_text(self, image, pos, text, text_size, text_color):
        '''
        draw chinese(or not) text with ttf
        :param image:     image(numpy.ndarray) to draw text
        :param pos:       where to draw text
        :param text:      the context, for chinese should be unicode type
        :param text_size: text size
        :param text_color:text color
        :return:          image
        '''
        # text='行人12312'
        p1 = (int(pos[0]), int(pos[1]))
        p2 = (int(pos[2]), int(pos[3]))
        if self.flag_rect:
            cv2.rectangle(image, p1, p2, self.rectcolor, thickness=self.lw, lineType=cv2.LINE_AA)
        tf = max(self.lw - 1, 1)  # font thickness
        w, h = cv2.getTextSize(text, 0, fontScale=self.lw / 3, thickness=tf)[0]  # text width, height
        outside = p1[1] - h >= 3
        p2 = p1[0] + int(w * 0.8), p1[1] - h - 3 if outside else p1[1] + h + 3
        cv2.rectangle(image, p1, p2, self.rectcolor, -1, cv2.LINE_AA)  # filled background

        self._face.set_char_size(text_size * self.size)
        metrics = self._face.size
        ascender = metrics.ascender / self.size

        # descender = metrics.descender/64.0
        # height = metrics.height/64.0
        # linegap = height - ascender + descender
        ypos = int(ascender)
        # pp3=(p1[0], p1[1] - 2 if outside else p1[1] + h + 2)
        # if not isinstance(text, unicode):
        #    text = text.decode('utf-8')
        img = self.draw_string(image, p1[0], p1[1], text, self.background)

        return img

    def draw_string(self, img, x_pos, y_pos, text, color):
        '''
        draw string
        :param x_pos: text x-postion on img
        :param y_pos: text y-postion on img
        :param text:  text (unicode)
        :param color: text color
        :return:      image
        '''
        prev_char = 0
        pen = freetype.Vector()
        pen.x = x_pos << int(math.log2(self.size))  # div 64
        pen.y = y_pos << int(math.log2(self.size))

        hscale = 1.0
        matrix = freetype.Matrix(int(hscale) * 0x10000, int(0.2 * 0x10000), \
                                 int(0.0 * 0x10000), int(1.1 * 0x10000))
        cur_pen = freetype.Vector()
        pen_translate = freetype.Vector()

        image = copy.deepcopy(img)
        for cur_char in text:
            self._face.set_transform(matrix, pen_translate)

            self._face.load_char(cur_char)
            kerning = self._face.get_kerning(prev_char, cur_char)
            pen.x += kerning.x
            slot = self._face.glyph
            bitmap = slot.bitmap

            cur_pen.x = pen.x
            cur_pen.y = pen.y - slot.bitmap_top * self.size
            self.draw_ft_bitmap(image, bitmap, cur_pen, color)

            pen.x += slot.advance.x
            prev_char = cur_char

        return image

    def draw_ft_bitmap(self, img, bitmap, pen, color):
        '''
        draw each char
        :param bitmap: bitmap
        :param pen:    pen
        :param color:  pen color e.g.(0,0,255) - red
        :return:       image
        '''
        x_pos = pen.x >> int(math.log2(self.size))
        y_pos = pen.y >> int(math.log2(self.size))
        cols = bitmap.width
        rows = bitmap.rows

        glyph_pixels = bitmap.buffer
        for row in range(rows):
            for col in range(cols):
                if glyph_pixels[row * cols + col] != 0:
                    if y_pos + row < len(img) and x_pos + col < len(img[0]):
                        img[y_pos + row][x_pos + col][0] = color[0]
                        img[y_pos + row][x_pos + col][1] = color[1]
                        img[y_pos + row][x_pos + col][2] = color[2]
                    else:
                        # logger.info(f' x_pos:{x_pos}  y_pos:{y_pos}  row:{row} col:{col}')
                        pass


### 定义标记类
class Drawer(object):
    ##  初始化接口
    def __init__(self, import_path=os.path.join(py_path, "common/dependency")):
        try:
            logger.info(f'标记类的版本号为:{Version_num}')
            self.import_path = import_path
            self.font_path = self.import_path + '/simsun.ttc'
            self.font = cv2.FONT_HERSHEY_SIMPLEX
            ##中英对照表全局标记名字
            self.global_label_name = alg_name
            self.imgwidth = 1920
            self.imgheight = 1080
            ### 绘制的字体 粗细 颜色等
            self.thickness = 2  ##划线的粗细
            self.fontScale = 1  ##字体大小
            self.colors = Colors()
            self.green = self.colors(5, True)
            self.blue = self.colors(11, True)
            self.red = self.colors(0, True)
            ### 默认框的颜色， 字体颜色
            self.labelcolor = self.green
            self.rectcolor = self.green
            self.linecolor = self.green
            # self.labelclass = Freetype2ch(self.import_path)   ##python freetype
            self.labelclass = FreetypePy(self.import_path)  ##python freetype
        except Exception as e:
            logger.info('标记类初始化错误!!!!!')
            logger.info(traceback.format_exc())

    ### 软件接口函数
    def draw_frame_box(self, frame, outmessage):
        t1 = cv2.getTickCount()
        flag = False
        try:
            outframe = self.draw_frame_main(frame, outmessage)
        except Exception as e:
            logger.info(traceback.format_exc())
            logger.info(f'!!!!!!!!!!!!!!!!!!!!!!!!标记类错误message:{outmessage}')
            outframe = frame
            flag = True

        t2 = cv2.getTickCount()
        #         logger.info(f'标记类时间:{1000*(t2-t1)/ cv2.getTickFrequency()} ms')
        return outframe, flag

    ### 标记类主函数
    def draw_frame_main(self, srcframe, srcmessage):
        dstframe = srcframe
        message = copy.deepcopy(srcmessage)

        ## 判断message是否要标记 error 为True 不标记 其他情况标记
        bFlag = self.Judgemessage(message)

        if not bFlag:
            return dstframe

        h, w = srcframe.shape[:2]
        self.imgwidth = w
        self.imgheight = h

        ## message进行过归一化处理，这里要还原回图像的参数
        message = self.Resizemessage(message)

        ## 标记矩形
        if message['lResults']["rect"]:
            dstframe = self.label_rect_message(dstframe, message)

        ## 标记跟踪
        if message['lResults']["track"]:
            dstframe = self.label_track_message(dstframe, message)

        ## 标记区域
        if message['lResults']["region"]:
            dstframe = self.label_region_message(dstframe, message)

        ## 标记线段
        if message['lResults']["line"]:
            dstframe = self.label_line_message(dstframe, message)

        ## 标记点
        if message['lResults']["point"]:
            dstframe = self.label_point_message(dstframe, message)

        return dstframe

    def Judgemessage(self, message):
        if message['error']:
            return False
        return True

    def Resizemessage(self, message):
        ## 1920*1080 是算法默认处理大小数据
        x_scale = self.imgwidth
        y_scale = self.imgheight

        lResults = message['lResults']
        if lResults['rect']:
            lResults['rect'] = [[x * x_scale, y * y_scale, w * x_scale, h * y_scale, c] for x, y, w, h, c in
                                lResults['rect']]
        if lResults['track']:
            lResults['track'] = [[x * x_scale, y * y_scale, w * x_scale, h * y_scale, n] for x, y, w, h, n in
                                 lResults['track']]
        if lResults['region']:
            for key in lResults['region'].keys():
                lResults['region'][key] = self.seg_diff_normalized(lResults['region'][key], x_scale, y_scale)
        if lResults['line']:
            lResults['line'] = [[x * x_scale, y * y_scale, w * x_scale, h * y_scale] for x, y, w, h in
                                lResults['line']]
        if lResults['point']:
            lResults['point'] = [[x * x_scale, y * y_scale, w * x_scale, h * y_scale, c] for x, y, w, h, c in
                                 lResults['point']]
        message['lResults'] = lResults

        return message

    def seg_diff_normalized(self, coords, x_scale, y_scale):
        normalized_coords = list(map(lambda shape: list(
            map(lambda points: list(map(lambda point: [point[0] * x_scale, point[1] * y_scale], points)), shape)),
                                     coords))
        return normalized_coords

    def label_rect_message(self, outimg, message):
        rects = list(message['lResults']["rect"])
        texts = list(message['lResults']["text"])
        bState= message['bState']
        # sValues = list(message['lResults']["sValue"])

        ###三种 仪表
        dialtypes = ['Digital', 'Pointer', 'Valve']
        ###仪表 定位
        locationtypes = ['DialLoc', 'HKIR']
        ###新老 车牌
        lprtypes = ['LPR', 'HLPR', 'CarJudge']
        ###人脸
        facetypes = ['FaceRec']
        ### 常规目标标记
        targettypes = ["SmogFire", "PersonCar", "IRPersonCar", "Sand", "Door", 'FireHydrant', "EQ", 'PersonandFace', \
                       "Car", 'DoorWindow', 'MeterBox', 'ChemicalDrip', 'Hat', 'Pothole', 'XJPersonCar', \
                       'Facelocal', 'LPRlocal', 'SmokeFire', "YoloWorld", "WorldRanging", "RetinaFace", "ArcFace", \
                       "MonkeyPerson","WarningClass"]

        if message["sType"] in dialtypes:
            self.labelcolor = self.green
            self.rectcolor = self.green
            for num, target_rect in enumerate(rects):
                label = texts[num][0]  ##标签
                iX = int(target_rect[0])
                iY = int(target_rect[1])
                iW = int(target_rect[2])
                iH = int(target_rect[3])
                position = (iX, iY, iX + iW, iY + iH)
                outimg = self.labelclass.DrawChinesename(outimg, label, position, self.rectcolor, self.labelcolor)
        elif message["sType"] in locationtypes:
            self.labelcolor = self.green
            self.rectcolor = self.green
            for num, target_rect in enumerate(rects):
                label = texts[num][0]  ##标签
                iX = int(target_rect[0])
                iY = int(target_rect[1])
                iW = int(target_rect[2])
                iH = int(target_rect[3])
                position = (iX, iY, iX + iW, iY + iH)
                if message["sType"] == 'HKIR':
                    # zh_label = str(round(sValues[num][0], 2)) + '_' + str(round(sValues[num][1], 2))  ##标签
                    zh_label = str(int(texts[num][0])) + '_' + str(int(texts[num][1]))  ##标签
                else:
                    zh_label = self.global_label_name[texts[num][0].split('_')[0]] + self.global_label_name[
                        texts[num][0].split('_')[1]]
                outimg = self.labelclass.DrawChinesename(outimg, zh_label, position, self.rectcolor, self.labelcolor)
        elif message["sType"] in lprtypes:
            self.labelcolor = self.blue
            self.labelclass.background = (0, 0, 0)
            self.rectcolor = self.green
            for num, target_rect in enumerate(rects):
                ## 特殊处理车辆入侵标记
                if message["sType"] == 'CarJudge':
                    if texts[0][num] == 'Warning':
                        self.rectcolor = self.red

                lpr_name = str(texts[num][0])  ##车牌
                iX = int(target_rect[0])
                iY = int(target_rect[1])
                iW = int(target_rect[2])
                iH = int(target_rect[3])
                position = (iX, iY, iX + iW, iY + iH)

                outimg = self.labelclass.DrawChinesename(outimg, lpr_name, position, self.rectcolor, self.labelcolor,
                                                         True)
        elif message["sType"] in facetypes and texts:
            self.labelcolor = self.green
            self.rectcolor = self.green
            for num, target_rect in enumerate(rects):
                name = texts[num][0]
                iX = int(target_rect[0])
                iY = int(target_rect[1])
                iW = int(target_rect[2])
                iH = int(target_rect[3])
                position = (iX, iY, iX + iW, iY + iH)
                if name == '访客':
                    self.rectcolor = self.red
                    self.labelcolor = self.red

                outimg = self.labelclass.DrawChinesename(outimg, name, position, self.rectcolor, self.labelcolor)
        elif message["sType"] in targettypes:
            warningstate = ['smoke', 'fire', 'person', 'open', 'car', 'no_hat', 'Pothole']
            for num, target_rect in enumerate(rects):
                if message["sType"] == 'PersonandFace':  ##行人人脸会出现行人框和人脸框数目不一致现象，故单独处理成person
                    name = 'person'
                else:
                    name = texts[num][0]
                ###名字属于报警状态颜色变成红色
                if name in warningstate  and message["sType"] != 'PersonandFace' :
                    self.labelcolor = self.red
                    self.rectcolor = self.red
                else:
                    self.labelcolor = self.green
                    self.rectcolor = self.green
                if bState:
                    self.labelcolor = self.red
                    self.rectcolor = self.red
                    
                try:
                    zh_name = self.global_label_name[name]
                except Exception as e:
                    zh_name = name
                iX = int(target_rect[0])
                iY = int(target_rect[1])
                iW = int(target_rect[2])
                iH = int(target_rect[3])
                position = (iX, iY, iX + iW, iY + iH)
                if message["sType"] == "arcface":
                    zh_name = name
                outimg = self.labelclass.DrawChinesename(outimg, zh_name, position, self.rectcolor, self.labelcolor)
        elif message["sType"] == 'WorkWear':
            ##功能38单独处理
            for bbox in rects:
                #         print(bbox)
                x, y, w, h, conf = bbox
                outimg = cv2.rectangle(outimg, (int(x), int(y)), (int(x + w), int(y + h)), (128, 0, 128), 2)  ##紫色框标记工装
        else:
            ##新增功能特殊处理
            for num, target_rect in enumerate(rects):
                name = texts[num][0]
                self.labelcolor = self.green
                self.rectcolor = self.green
                try:
                    zh_name = self.global_label_name[name]
                except Exception as e:
                    zh_name = name
                iX = int(target_rect[0])
                iY = int(target_rect[1])
                iW = int(target_rect[2])
                iH = int(target_rect[3])
                position = (iX, iY, iX + iW, iY + iH)
                outimg = self.labelclass.DrawChinesename(outimg, zh_name, position, self.rectcolor, self.labelcolor)
            pass

        return outimg

    def label_region_message(self, outimg, message):

        if message['sType'] == 'FireHydrant' or message['sType'] == 'ChemicalDrip' or message[
            'sType'] == 'IndoorFlooding':
            ## 循环region 进行标记
            for key in message['lResults']["region"].keys():
                reg = message['lResults']["region"][key]
                if len(reg) != 0:
                    reg = [cv2.UMat(np.array(cn).astype("int")) for cn in reg]
                    if key == "seg":
                        if message['sType'] == 'FireHydrant':
                            outimg = cv2.drawContours(image=outimg, contours=reg, contourIdx=-1, color=self.green,
                                                      thickness=self.thickness)
                        else:
                            outimg = cv2.drawContours(image=outimg, contours=reg, contourIdx=-1, color=self.red,
                                                      thickness=self.thickness)
                    elif key == "diff":
                        outimg = cv2.drawContours(image=outimg, contours=reg, contourIdx=-1, color=self.blue,
                                                  thickness=self.thickness)
                    outimg = np.asarray(outimg.get())

        return outimg

    def label_track_message(self, outimg, message):
        rects = list(message['lResults']["rect"])
        tracks = list(message['lResults']["track"])
        texts = list(message['lResults']["text"])

        ##行人和人脸标记
        if message["sType"] == 'PersonandFace':
            self.rectcolor = self.red

            ###标记人脸框
            for num, track_rect in enumerate(tracks):
                name = texts[num][0]
                iX = int(track_rect[0])
                iY = int(track_rect[1])
                iW = int(track_rect[2])
                iH = int(track_rect[3])
                position = (iX, iY, iX + iW, iY + iH)
                if name == '访客':
                    self.rectcolor = self.red
                else:
                    self.rectcolor = self.green

                outimg = self.labelclass.DrawChinesename(outimg, name, position, self.rectcolor, self.labelcolor)

        ##行人跟踪及热成像行人跟踪及车辆跟踪
        tracktypes = ['PersonTrack', 'IRPersonTrack', 'CarTrack']
        if message["sType"] in tracktypes:
            ###标记跟踪框即可
            self.rectcolor = self.green
            for num, track_rect in enumerate(tracks):
                name = texts[num][0]
                zh_name = self.global_label_name[name]
                iX = int(track_rect[0])
                iY = int(track_rect[1])
                iW = int(track_rect[2])
                iH = int(track_rect[3])
                labelnum = int(track_rect[4])
                position = (iX, iY, iX + iW, iY + iH)
                outimg = self.labelclass.DrawChinesename(outimg, zh_name, position, self.rectcolor, self.labelcolor)
                cv2.putText(outimg, str(labelnum), (iX + iW - 50, iY), self.font, self.fontScale, self.red,
                            2 * self.thickness)

        if message["sType"] == 'FaceTrack':
            ###标记跟踪框即可
            self.rectcolor = self.green
            for num, track_rect in enumerate(tracks):
                name = ' '
                iX = int(track_rect[0])
                iY = int(track_rect[1])
                iW = int(track_rect[2])
                iH = int(track_rect[3])
                labelnum = int(track_rect[4])

                position = (iX, iY, iX + iW, iY + iH)
                outimg = self.labelclass.DrawChinesename(outimg, name, position, self.rectcolor, self.labelcolor)
                cv2.putText(outimg, str(labelnum), (iX + iW - 50, iY), self.font, self.fontScale, self.red,
                            2 * self.thickness)

        if message["sType"] == 'workwear':
            for num, bbox in enumerate(tracks):
                if texts[num] == 'warning':
                    color = (0, 0, 255)
                elif texts[num] == 'ok':
                    color = (0, 255, 0)
                else:
                    color = (0, 255, 255)
                x, y, w, h, label = bbox
                cv2.rectangle(outimg, (int(x), int(y)), (int(x + w), int(y + h)), color, 2)
                ##红色标记行人
                cv2.putText(outimg, str(label), (int(x), int(y) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 3)

        return outimg

    def label_line_message(self, outimg, message):
        lines = list(message['lResults']["line"])
        sValues = list(message['lResults']["text"])
        if message["sType"] == 'Mesh':
            for num, target_line in enumerate(lines):
                label = sValues[num][0]  ##标签
                if label == 'Warning':
                    self.linecolor = self.red
                    self.labelcolor = self.red
                    self.rectcolor = self.red
                else:
                    self.linecolor = self.green
                    self.labelcolor = self.green
                    self.rectcolor = self.green
                zh_label = self.global_label_name[label]
                p1 = (int(target_line[0]), int(target_line[1]))
                p2 = (int(target_line[2]), int(target_line[3]))
                cv2.line(outimg, p1, p2, self.linecolor, self.thickness)
                position = (int(target_line[0]), int(target_line[1]), int(target_line[2]), int(target_line[3]))
                outimg = self.labelclass.DrawChinesename(outimg, zh_label, position, self.rectcolor, self.labelcolor,
                                                         flag_rect=False)

        return outimg

    def label_point_message(self, outimg, message):
        points = list(message['lResults']["point"])

        return outimg


if __name__ == "__main__":
    # ## 仪表
    # outmessage={
    # "error": False  ,                 
    # "bFlag": True,           
    # "bState": False ,                
    # "sType": "Valve",    ##  Pointer           
    # "sValue": '0000',                
    # "lResults": {
    #             "rect":  [[0.1, 0.1, 0.2, 0.2, 0.5],[0.6, 0.3, 0.1, 0.3, 0.5],[0.8, 0.6, 0.1, 0.2, 0.5]],            
    #             "track":  [],
    #             "region":[],
    #             "line":[],
    #             "point":[],
    #             "text":[],
    #             "sValue":[['1231'],['2147'],['3215']],        
    #             # "sValue":[['left_up'],['ok_ok'],['right_down']],        
    #             "res_key":"rect",            
    #             }
    # }

    # # 仪表定位
    # outmessage={
    #     'error': False, 
    #     'bFlag': True, 
    #     'bState': False, 
    #     'sType': 'DialLoc', 
    #     'sValue': 'ok_ok', 
    #     'lResults': {
    #         'rect': [[0.4171875, 0.33611111111111114, 0.13541666666666666, 0.2388888888888889, 0.912616]], 
    #         'track': [], 'region': [], 'line': [], 'point': [], 'text': [], 
    #         'sValue': [['ok_ok']], 
    #         'res_key': 'rect'
    #         }
    # }

    #  ##画框
    outmessage = {
        "error": False,
        "bFlag": True,
        "bState": False,
        "sType": "Door",
        "sValue": '3',
        "lResults": {
            "rect": [[0.1, 0.1, 0.2, 0.2, 0.5], [0.6, 0.3, 0.1, 0.3, 0.5], [0.8, 0.6, 0.1, 0.2, 0.5]],
            "track": [],
            "region": [],
            "line": [],
            "point": [],
            "text": [['close'], ['close'], ['open']],
            "sValue": [],
            "res_key": "rect",
        }
    }

    ## 器材点
    # outmessage={
    #     'error': False, 
    #     'bFlag': True, 
    #     'bState': False, 
    #     'sType': 'EQ', 
    #     'sValue': '14', 
    #     'lResults': {
    #         'rect': [[0.0005208333333333333, 0.39166666666666666, 0.06145833333333333, 0.2555555555555556, 0.951262], [0.06041666666666667, 0.39166666666666666, 0.06354166666666666, 0.26666666666666666, 0.949899], [0.11562499999999999, 0.41203703703703703, 0.03958333333333333, 0.2564814814814815, 0.824953], [0.11458333333333333, 0.6675925925925926, 0.030729166666666665, 0.13796296296296298, 0.96844], [0.040625, 0.6574074074074074, 0.0484375, 0.14537037037037037, 0.966539], [0.0, 0.65, 0.015104166666666667, 0.14907407407407408, 0.905726], [0.3833333333333333, 0.41203703703703703, 0.05260416666666667, 0.37962962962962965, 0.967439], [0.31875, 0.40925925925925927, 0.05677083333333333, 0.3944444444444445, 0.962185], [0.45416666666666666, 0.412962962962963, 0.05260416666666667, 0.3851851851851852, 0.960217], [0.6015625, 0.4027777777777778, 0.033854166666666664, 0.19351851851851853, 0.95611], [0.5359375, 0.40092592592592596, 0.034375, 0.19814814814814816, 0.955612], [0.53125, 0.6787037037037037, 0.12916666666666665, 0.075, 0.948636], [0.5328125, 0.6018518518518519, 0.12604166666666666, 0.07037037037037037, 0.946663], [0.5333333333333333, 0.7611111111111112, 0.12604166666666666, 0.05648148148148149, 0.941996]],
    #         'track': [], 
    #         'region': [], 
    #         'line': [], 
    #         'point': [], 
    #         'text': [['axe'], ['axe'], ['axe'], ['exting'], ['exting'], ['exting'], ['shovel'], ['shovel'], ['shovel'], ['shovel'], ['shovel'], ['sandbox'], ['sandbox'], ['sandbox']], 
    #         'sValue': [], 
    #         'res_key': 'rect'
    #         }
    #     }

    ## 铁丝网
    # outmessage={
    #     'error': False, 
    #     'bFlag': True, 
    #     'bState': False, 
    #     'sType': 'Mesh', 
    #     'sValue': '', 
    #     'lResults': {
    #         'rect': [], 
    #         'track': [], 
    #         'region': [], 
    #         'line': [[0.0, 0.201466903090477, 0.26700034737586975, 0.19706545770168304], [0.619051456451416, 0.2117728590965271, 0.9985561966896057, 0.217681884765625], [0.006898894906044006, 0.4693266451358795, 0.25119149684906006, 0.46062731742858887], [0.699612021446228, 0.501686155796051, 0.9954957365989685, 0.5053055286407471], [0.005488596856594086, 0.7536256909370422, 0.2517991364002228, 0.7470333576202393], [0.6869162321090698, 0.7705187797546387, 0.9926260709762573, 0.7676746845245361]], 
    #         'point': [], 
    #         'text': [], 
    #         'sValue': [['Warning'], ['Warning'], ['Warning'],['Normal'], ['Normal'], ['Normal']], 
    #         'res_key': ''
    #         }
    #     }

    # ## 消防漏水
    # outmessage={
    #     'error': False, 
    #     'bFlag': True, 
    #     'bState': True, 
    #     'sType': 'FireHydrant', 
    #     'sValue': 5, 
    #     'lResults': {
    #         'rect': [[0.33557939529418945, 0.06030089766890914, 0.0087890625, 0.040277749520761, 0.29736328125], [0.35149736404418946, 0.06359950878002026, 0.013671875, 0.038541638409649887, 0.2486572265625], [0.03620198170344035, 0.06168978655779803, 0.0111572265625, 0.038194416187427666, 0.29736328125], [0.05191243092219035, 0.05908561989113137, 0.011669921875, 0.04062497174298322, 0.1268310546875], [0.28548173904418944, 0.0689814532244647, 0.2894530932108561, 0.9013887758608218, 0.9423828125]], 
    #         'track': [], 
    #         'region': {
    #             'seg': [[[[0.3515625, 0.6157407407407408]], [[0.3515625, 0.6222222222222222]], [[0.3520833333333333, 0.6222222222222222]], [[0.3520833333333333, 0.6157407407407408]]], [[[0.346875, 0.5740740740740741]], [[0.3463541666666667, 0.5750000000000001]], [[0.3463541666666667, 0.5768518518518518]], [[0.3458333333333333, 0.5777777777777778]], [[0.3458333333333333, 0.5787037037037037]], [[0.3463541666666667, 0.5796296296296296]], [[0.3463541666666667, 0.5814814814814815]], [[0.346875, 0.5824074074074075]], [[0.346875, 0.5842592592592593]], [[0.34739583333333335, 0.5851851851851853]], [[0.34739583333333335, 0.5861111111111111]], [[0.34791666666666665, 0.587037037037037]], [[0.34791666666666665, 0.5898148148148148]], [[0.3484375, 0.5907407407407408]], [[0.3484375, 0.5935185185185186]], [[0.3489583333333333, 0.5944444444444444]], [[0.3489583333333333, 0.5953703703703704]], [[0.3494791666666667, 0.5962962962962963]], [[0.3494791666666667, 0.5981481481481482]], [[0.35, 0.5990740740740741]], [[0.35, 0.600925925925926]], [[0.35052083333333334, 0.6018518518518519]], [[0.35052083333333334, 0.6037037037037037]], [[0.35104166666666664, 0.6046296296296296]], [[0.35104166666666664, 0.6064814814814815]], [[0.3515625, 0.6074074074074074]], [[0.3515625, 0.6092592592592593]], [[0.3520833333333333, 0.6101851851851852]], [[0.35260416666666666, 0.6101851851851852]], [[0.3536458333333333, 0.6083333333333334]], [[0.3536458333333333, 0.6074074074074074]], [[0.3541666666666667, 0.6064814814814815]], [[0.3541666666666667, 0.6037037037037037]], [[0.3546875, 0.6027777777777777]], [[0.3546875, 0.5851851851851853]], [[0.3541666666666667, 0.5842592592592593]], [[0.3541666666666667, 0.5814814814814815]], [[0.3536458333333333, 0.5805555555555556]], [[0.3536458333333333, 0.5796296296296296]], [[0.35260416666666666, 0.5777777777777778]], [[0.3520833333333333, 0.5777777777777778]], [[0.35, 0.5740740740740741]]]],
    #             'diff': []
    #             },
    #         'line': [], 
    #         'point': [], 
    #         'text': [['person'], ['person'], ['person'], ['person'], ['fire hydrant']], 
    #         # "text":[['drip'],['drip'],['drip'],['drip'],['drip']],
    #         'sValue': [], 
    #         'res_key': 'rect'
    #         }
    #     }

    ##行人人脸
    # outmessage={
    #     'error': False, 
    #     'bFlag': True, 
    #     'bState': True, 
    #     'sType': 'PersonandFace',
    #     'sValue': '', 
    #     'lResults': {
    #         'rect': [[0.5661458333333333, 0.2351851851851852, 0.2609375, 0.7648148148148148, 0.935496], [0.1671875, 0.2833333333333333, 0.20833333333333334, 0.7166666666666667, 0.923304]], 
    #         'track': [[0.2598958333333333, 0.3574074074074074, 0.059375, 0.14351851851851852, 566]], 
    #         'region': [], 
    #         'line': [], 
    #         'point': [], 
    #         'text': [['赵']], 
    #         'sValue': [], 
    #         'res_key': ''
    #         }
    #     }

    #  普通跟踪
    # outmessage={
    #     'error': False,
    #     'bFlag': True,
    #     'bState': False,
    #     'sType': 'CarTrack',
    #     'sValue': '', 
    #     'lResults': {
    #         'rect': [[0.4666666666666667, 0.3472222222222222, 0.20572916666666666, 0.6287037037037038, 0.888175], [0.9026041666666667, 0.39537037037037037, 0.09739583333333333, 0.2351851851851852, 0.850627], [0.06666666666666667, 0.4342592592592593, 0.31197916666666664, 0.5407407407407407, 0.70558]], 
    #         'track': [[0.065625, 0.4342592592592593, 0.31354166666666666, 0.5398148148148149, 287], [0.4666666666666667, 0.3462962962962963, 0.20520833333333333, 0.6296296296296297, 288], [0.9026041666666667, 0.3944444444444445, 0.096875, 0.2351851851851852, 289]], 
    #         'region': [], 
    #         'line': [], 
    #         'point': [], 
    #         'text': [['car'], ['car'], ['car']], 
    #         'sValue': [], 
    #         'res_key': ''
    #         }
    #     }

    # ## 车牌
    # outmessage={
    #     'error': False, 
    #     'bFlag': True, 
    #     'bState': False, 
    #     'sType': 'LPR', 
    #     'sValue': 2, 
    #     'lResults': {
    #         'rect': [[0.8375, 0.6092592592592593, 0.12604166666666666, 0.07777777777777778, 0.99995345], [0.165625, 0.5268518518518519, 0.12864583333333332, 0.07777777777777778, 0.9078067]], 
    #         'track': [], 
    #         'region': [], 
    #         'line': [], 
    #         'point': [], 
    #         'text': [['Normal', 'Warning']], 
    #         'sValue': [['宁A96A01'], ['赣F295Q9']], 
    #         'res_key': ''
    #     }
    # }

    outmessage = {'error': False, 'bFlag': True, 'bState': True, 'sType': 'IRPerson', 'sValue': '1', 'lResults': {
        'rect': [[0.17447916666666666, 0.49166666666666664, 0.23697916666666666, 0.1824074074074074, 4.552219]],
        'track': [], 'region': [], 'line': [], 'point': [], 'text': [['car']], 'sValue': [], 'res_key': 'rect'}}
    # outmessage={
    #     'error': False,
    #     'bFlag': True,
    #     'bState': True,
    #     'sType': 'IRPerson',
    #     'sValue': 3,
    #     'lResults': {
    #         'rect': [[0.2703125, 0.47604166666666664,0.5773437500000002,0.5239583333333333,5.885776],[0.45546875000000003,0.06145833333333333,0.0578125,0.06041666666666667,2.864319]],
    #         'track': [],
    #         'region': [],
    #         'line': [],
    #         'point': [],
    #         'text': [['person','car']],
    #         'sValue': [],
    #         'res_key': 'rect'
    #         }
    #     } 

    img = cv2.imread('1.jpg')
    drawer = Drawer()

    while True:
        outimg, _ = drawer.draw_frame_box(img, outmessage)
        cv2.namedWindow("1", 0)
        cv2.imshow('1', outimg)
        cv2.waitKey(10)
