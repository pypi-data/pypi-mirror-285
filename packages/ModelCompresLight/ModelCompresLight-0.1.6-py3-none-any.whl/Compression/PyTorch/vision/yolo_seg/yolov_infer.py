# -*- coding: utf-8 -*- #
import os

from ultralytics import YOLO
import cv2
import numpy as np
import json
import base64
model = YOLO('best.pt')  # build from YAML and transfer weights


"""
from ultralytics import YOLO





model = YOLO('yolov8s-seg.yaml').load('yolov8s-seg.pt')  # build from YAML and transfer weights



results = model.train(data='model.yaml', epochs=20, imgsz=512,device='0',batch=8,
                      name='./run/300_512')



"""




def image_to_base64(image):
    # 读取图片


    # 将图片编码为字节码
    _, buffer = cv2.imencode('.png', image)
    byte_data = buffer.tobytes()

    # 将字节码编码为Base64字符串
    base64_image = base64.b64encode(byte_data).decode('utf-8')

    return base64_image



#["Road line","Road","Car","Traffic sign"]
jsonresults={}
check_dict=[6,7,10,12]
imgs=os.listdir('9500')
for e in imgs:
    results = model.predict(os.path.join('el500',e),
                            save=False,
                            name="pp",conf=0.2)  # predict on an image
    # model.export(format='onnx',imgsz=416)

    label_mask=np.zeros(shape=(600,800))

    for result in results:
        boxes = result.boxes  # Boxes object for bbox outputs
        print("--------",boxes,result.probs)
        masks=result.masks.cpu().numpy()

        for mask,box in zip(masks.data,result.boxes):
            # mask_th=np.where(mask>0.5,1,0)
            # mask_=np.transpose(mask, [1,0])
            mask_2=cv2.resize(mask,(800,600))
            cls=box.cls.cpu().numpy()
            maak_vl=check_dict[int(cls[0])]

            label_mask[mask_2==1]=maak_vl

        # outImage = np.transpose(mask.data,[2,1,0])
        # cv2.imwrite('outImage.jpg',outImage*255)

        #
        # outImage = np.argmax(outImage, axis=2)
        # outImage=outImage*60
    # cv2.imwrite('tmp.jpg',label_mask*20)


    # print(print(results[0]))
    # print(results[0].logits.cpu().detach().numpy()*81)



    encode_binary_mask_ = image_to_base64(label_mask)

    jsonresults[e] = encode_binary_mask_

save2json = json.dumps(jsonresults, indent=4)

with open('predict.json', 'w') as fw:
    fw.write(save2json)












