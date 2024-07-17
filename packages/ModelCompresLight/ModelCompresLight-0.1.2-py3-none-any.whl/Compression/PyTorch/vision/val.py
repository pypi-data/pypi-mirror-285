# -*- coding: utf-8 -*- #

import numpy as np
import torch
import matplotlib.pyplot as plt
import cv2
import json
import os
import base64
model_path = 'i_84.pt'

if torch.cuda.is_available():
    model = torch.load(model_path)
else:
    model = torch.load(model_path, map_location=torch.device('cpu'))

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")  # xm.xla_device()
# print(device)
# Set the model to evaluate mode
model.eval()

imgs='label500'

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
    img = cv2.resize(originalImage, (512, 512), cv2.INTER_AREA).transpose(2, 0, 1)
    img = img.reshape(1, 3, img.shape[1], img.shape[2])



    with torch.no_grad():
    #     a = model(torch.from_numpy(img).to(device).type(torch.FloatTensor)/255)
        if torch.cuda.is_available():
            a = model(torch.from_numpy(img).to(device).type(torch.cuda.FloatTensor)/255)
        else:
            a = model(torch.from_numpy(img).to(device).type(torch.FloatTensor)/255)
    #


    # outImage = a['out'].cpu().detach().numpy()[0]
    outImage = a.cpu().detach().numpy()[0]

    outImage=outImage.transpose(1,2,0)
    # cv2.imwrite('outImage.jpg',outImage*255)

    #
    outImage=np.argmax(outImage,axis=2)

    values_to_check = [0, 6, 7, 10, 12]

    # step2

    # 使用numpy.isin创建一个布尔索引数组
    oen_img_gt_img_condition = np.isin(outImage, values_to_check)

    # 使用numpy.where根据条件替换元素
    oen_img_gt_img_condition_res = np.where(oen_img_gt_img_condition, outImage, 0)
    print("has_value",np.unique(oen_img_gt_img_condition_res))

    encode_binary_mask_ = image_to_base64(oen_img_gt_img_condition_res)
    cv2.imwrite(os.path.join("./outs",e),oen_img_gt_img_condition_res)
    jsonresults[e] = encode_binary_mask_

save2json = json.dumps(jsonresults, indent=4)

with open('6000.json', 'w') as fw:
    fw.write(save2json)

#
# fig, arr=plt.subplots(1,3, figsize=(10,10))
#
# arr[0].imshow(cv2.resize(originalImage, (512, 512)))
# arr[0].set_title('Original Image')
# arr[0].axis('off')
# arr[1].imshow(cv2.resize(cv2.imread('xx.png'), (256, 256))[:,:,2])
# arr[1].set_title('True Mask')
# arr[1].axis('off')
# arr[2].imshow(outImage)
# arr[2].set_title('Predicted Mask')
# arr[2].axis('off')
# plt.savefig('xx.jpg')
