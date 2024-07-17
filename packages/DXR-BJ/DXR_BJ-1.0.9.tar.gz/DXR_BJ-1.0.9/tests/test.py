
from DXR_BJ import drawer

import cv2
import time
draw=drawer.Drawer('./')
img=cv2.imread('1.jpg')
# res={'10': {'error': False, 'bFlag': True, 'bState': True, 'sType': 'IRPerson', 'cnType': '热成像行人检测', 'sValue': '1', 'lResults': {'rect': [[0.4, 0.001851851851851852, 0.515625, 0.9944444444444445, 0.557663]], 'track': [], 'region': [], 'line': [], 'point': [], 'text': [['person']], 'sValue': '1', 'res_key': 'rect'}}, '17': {'error': False, 'bFlag': True, 'bState': False, 'sType': 'HKIR', 'cnType': '温度监控', 'sValue': '0', 'lResults': {'rect': [], 'track': [], 'region': [], 'line': [], 'point': [], 'text': [], 'sValue': '', 'res_key': 'rect'}}}
# outmessage={'error': False, 'bState': True, 'sType': 'zx', 'cnType': '', 'sValue': '1', 'lResults': {'rect': [[0.4745, 0.2648, 0.1005, 0.2231, 0.9996]], 'track': [], 'region': [], 'line': [], 'point': [], 'text': [['111']], 'res_key': 'rect'}}
outdata={'9': {'error': False, 'bState': True, 'sType': 'PersonCar', 'cnType': '人车检测', 'sValue': '目标数量2', 'lResults': {'rect': [[0.3524, 0.4332, 0.1253, 0.3781, 0.6733], [0.4953, 0.4254, 0.1164, 0.3852, 0.8335]], 'track': [], 'region': [], 'line': [], 'point': [], 'text': [['person'], ['person']], 'res_key': 'rect'}}, '40': {'error': False, 'bState': True, 'sType': 'ArcFace', 'cnType': '人脸识别', 'sValue': '2', 'lResults': {'rect': [[0.3524+0.1, 0.4332+0.1, 0.1253+0.1, 0.3781+0.1, 0.6733], [0.5266+0.1, 0.45+0.1, 0.025+0.1, 0.0537+0.1, -0.6]], 'track': [[0.2328, 0.3407, 0.362, 0.6583, 5], [0.5005, 0.4352, 0.076, 0.2722, 7]], 'region': [], 'line': [], 'point': [], 'text': [['访客'], ['访客']], 'res_key': 'rect'}}}
num = 0
while True:
    for key in outdata:
        outmessage=outdata[key]
        outframe,_= draw.draw_frame_box(img, outmessage)
        # break
        if num !=0:
            img=outframe
        num=num+1
    # print(f'标记时间:{1000*(time.time()-t1)}')
    cv2.imshow('1',outframe)
    cv2.waitKey(10)
