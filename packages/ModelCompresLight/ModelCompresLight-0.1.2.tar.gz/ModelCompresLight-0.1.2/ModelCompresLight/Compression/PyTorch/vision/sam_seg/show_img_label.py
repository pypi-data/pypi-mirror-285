# -*- coding: utf-8 -*- #

import numpy as np
import torch
import matplotlib
import matplotlib.pyplot as plt
import cv2
import json
matplotlib.use('Agg')
import os
import base64

imgs_root='imgs'
imgs_root_mask='gts'

for e in os.listdir(imgs_root):

    img0Path=os.path.join(imgs_root,e)

    img0=cv2.imread(img0Path)
    fig, arr=plt.subplots(1,2, figsize=(20,20))

    arr[0].imshow(cv2.resize(img0, (512, 512)))
    arr[0].set_title('Original Image')
    arr[0].axis('off')

    img_mask=cv2.imread(os.path.join(imgs_root_mask,e))

    values_to_check = [-1, 6, 7, 8, 13]

    # step2

    # 使用numpy.isin创建一个布尔索引数组
    oen_img_gt_img_condition = np.isin(img_mask, values_to_check)

    # 使用numpy.where根据条件替换元素
    oen_img_gt_img_condition_res = np.where(oen_img_gt_img_condition, img_mask, 0)
    oen_img_gt_img_condition_res=cv2.resize(oen_img_gt_img_condition_res,(512,512),interpolation=cv2.INTER_NEAREST)[:,:,2]
    arr[1].imshow(oen_img_gt_img_condition_res)
    arr[1].set_title('True Mask')
    arr[1].axis('off')

    plt.savefig(os.path.join('labeled',e))

