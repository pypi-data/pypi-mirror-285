# -*- coding: utf-8 -*-
"""

"""

import xml.etree.ElementTree as ET
import pickle
import os
import cv2
from os import listdir, getcwd
from os.path import join

classes=["person"]


def convert(size, box):
    #coco-->
    #        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))

    dw = 1./(size[0])
    dh = 1./(size[1])
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)
def convert_annotation(file,name):
    in_file = open(file)  #将数据集放于当前目录下
    out_file = open(result_path +'/%s.txt'%(name), 'w')
    print(result_path +'/%s.txt'%(name))
    tree=ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    # w = int(size.find('width').text)
    # h = int(size.find('height').text)
    for obj in root.iter('object'):
        # difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes:
            continue
        # if cls not in classes or int(difficult)==1:
        #     continue
        if cls in classes:
            pass
        else:
            print("cls-not-------------------------------?",cls)
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        x1 = b[0]
        y1 = b[2]
        x2 = b[1]
        y2 = b[3]

        if x1 < 0 or y1 < 0 or x2 > width or y2 > height:
            continue
        bb = convert((width,height), b)
        print("writing:",str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')



result_path = '../data/toy/labels/val/'
if not os.path.exists(result_path):
    os.makedirs(result_path)

root_path = '../data/toy/annotations/val/'

for file in os.listdir(root_path):
    anno_path = root_path  + file
    image_path = './images/' + file.split('.')[0] + '.jpg'


    im = cv2.imread(image_path)
    try:
        height,width,c = im.shape
    except:
        print(anno_path)

    print("height---------------------------------->",height)
    name = file.split('.xml')[0]
    convert_annotation(anno_path,name)

