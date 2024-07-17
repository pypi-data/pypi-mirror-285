# -*- coding: utf-8 -*- #

import numpy as np
import torch
import matplotlib.pyplot as plt
import cv2
import json
import os
import base64
model_path = '5epochs_weights.pt'

if torch.cuda.is_available():
    model = torch.load(model_path)
else:
    model = torch.load(model_path, map_location=torch.device('cpu'))

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")  # xm.xla_device()
# print(device)
# Set the model to evaluate mode
model.eval()

imgs='images'

jsonresults={}

def image_to_base64(image):
    # 读取图片


    # 将图片编码为字节码
    _, buffer = cv2.imencode('.png', image)
    byte_data = buffer.tobytes()

    # 将字节码编码为Base64字符串
    base64_image = base64.b64encode(byte_data).decode('utf-8')

    return base64_image



for e in os.listdir(imgs):
    # img=cv2.imread(os.path.join(imgs,e))

    originalImage = cv2.imread(os.path.join(imgs,e))
    img = cv2.resize(originalImage, (800, 600), cv2.INTER_AREA).transpose(2, 0, 1)
    img = img.reshape(1, 3, img.shape[1], img.shape[2])



    with torch.no_grad():
    #     a = model(torch.from_numpy(img).to(device).type(torch.FloatTensor)/255)
        if torch.cuda.is_available():
            a = model(torch.from_numpy(img).to(device).type(torch.cuda.FloatTensor)/255)
        else:
            a = model(torch.from_numpy(img).to(device).type(torch.FloatTensor)/255)
    #


    outImage = a['out'].cpu().detach().numpy()[0]

    outImage=outImage.transpose(1,2,0)
    # cv2.imwrite('outImage.jpg',outImage*255)

    #
    outImage=np.argmax(outImage,axis=2)

    outImage_800_600=cv2.resize(outImage,(800,600),interpolation=cv2.INTER_NEAREST)
    # print("has_value",np.unique(outImage))

    outImage_800_600_ch3=np.zeros(shape=(600,800,3))
    outImage_800_600_ch3[:,:,2]=outImage_800_600

    # print("outImage_800_600_ch3", np.unique(outImage))
    cv2.imwrite(os.path.join('auto_label',e),outImage_800_600_ch3)


