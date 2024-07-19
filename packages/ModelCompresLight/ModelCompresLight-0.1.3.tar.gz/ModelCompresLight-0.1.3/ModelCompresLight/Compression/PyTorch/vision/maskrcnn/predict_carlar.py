import os

import torch
import matplotlib
matplotlib.use('TkAgg')
import pytorch_mask_rcnn as pmr
import numpy as np
use_cuda = True
dataset = "ds"
ckpt_path = "1020"
import cv2
import json
from PIL import Image
import base64
device = torch.device("cuda:1" if torch.cuda.is_available() and use_cuda else "cpu")
if device.type == "cuda":
    pmr.get_gpu_prop(show=True)
print("\ndevice: {}".format(device))


classes=4
model = pmr.maskrcnn_resnet50(True, classes + 1).to(device)
# model = pmr.maskrcnn_resnet101(True, classes + 1).to(device)

model.eval()
model.head.score_thresh = 0.2

if ckpt_path:
    checkpoint = torch.load(ckpt_path, map_location=device)
    model.load_state_dict(checkpoint["model"])
    # model.load_state_dict(checkpoint.state_dict())

    del checkpoint
jsonresults={}
def image_to_base64(image):
    # 读取图片


    # 将图片编码为字节码
    _, buffer = cv2.imencode('.png', image)
    byte_data = buffer.tobytes()

    # 将字节码编码为Base64字符串
    base64_image = base64.b64encode(byte_data).decode('utf-8')

    return base64_image
def img(root_img_path):
    #

    root_imgs =root_img_path

    image_ori = Image.open(root_imgs).convert("RGB")
    from torchvision import transforms
    # normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    image = transforms.ToTensor()(image_ori).to(device)
    # image=normalize(image)

    with torch.no_grad():
        result = model(image)
        print(image.size())
        print(result['boxes'].size())

        boxes = result["boxes"] if "boxes" in result else None
        scores = result["scores"] if "scores" in result else None
        classes = result["labels"] if "labels" in result else None
        masks = result["masks"] if "masks" in result else None
        # print(result['masks'])


        print("classesclasses",scores,classes)

        image_ori = cv2.cvtColor(np.asarray(image_ori), cv2.COLOR_RGB2BGR)

        masked_image = np.array(image_ori,np.uint8)
        print('masked_image_shape',masked_image.shape)
        # plotted = plot_masks(image_ori, result, classes)
        tt={1:6,2:7,3:10,4:12}

        mask_img=None
        for idx,box in enumerate(boxes):
            xmin=box[0]
            ymin=box[1]
            xmax=box[2]
            ymax=box[3]
            print()
            if scores[idx]>0.5:
                cv2.rectangle(image_ori, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color=(0, 255, 0), thickness=3)
                if isinstance(mask_img,(np.ndarray,)):
                # if mask_img.any():
                    mask = masks[idx,:, :].cpu().detach().numpy()
                    mask_img_pre=np.where(mask>0.15,tt[classes[idx].cpu().numpy().tolist()],0)

                    values_to_check = [tt[classes[idx].cpu().numpy().tolist()]]

                    # step2

                    # 使用numpy.isin创建一个布尔索引数组
                    oen_img_gt_img_condition = np.isin(mask_img_pre, values_to_check)

                    # 使用numpy.where根据条件替换元素
                    # mask_img = np.where(oen_img_gt_img_condition, mask_img, 0)

                    mask_img[oen_img_gt_img_condition]=tt[classes[idx].cpu().numpy().tolist()]

                else:
                    tp= masks[idx,:, :].cpu().detach().numpy()
                    mask_img =np.where(tp>0.15,tt[classes[idx].cpu().numpy().tolist()],0)

        print('mask_imgmask_imgmask_img',np.unique(mask_img),mask_img.shape)

        encode_binary_mask_ = image_to_base64(mask_img)

        jsonresults[e] = encode_binary_mask_
        return mask_img





root="7500"
for e in os.listdir(root):
    pp=os.path.join(root,e)


    img(pp)


#
save2json = json.dumps(jsonresults, indent=4)

with open('15.json', 'w') as fw:
    fw.write(save2json)
