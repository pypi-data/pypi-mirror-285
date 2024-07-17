import torch
import pytorch_mask_rcnn as pmr
import numpy as np
use_cuda = True
dataset = "dianshi"
ckpt_path = "/home/hanjianhui/Testingcodes/Pytorch_mrcnns/PyTorch-Simple-MaskRCNN-res101/weights/101_123_512_weights/-20"
import cv2
from PIL import Image

device = torch.device("cuda:1" if torch.cuda.is_available() and use_cuda else "cpu")
if device.type == "cuda":
    pmr.get_gpu_prop(show=True)
print("\ndevice: {}".format(device))


classes=2
# model = pmr.maskrcnn_resnet50(True, classes + 1).to(device)
model = pmr.maskrcnn_resnet101(True, classes + 1).to(device)

model.eval()
model.head.score_thresh = 0.2

if ckpt_path:
    checkpoint = torch.load(ckpt_path, map_location=device)
    model.load_state_dict(checkpoint["model"])
    # model.load_state_dict(checkpoint.state_dict())

    del checkpoint


def img():
    #
    """
    /home/hanjianhui/Testingcodes/Pytorch_mrcnns/Mask-RCNN-pytorchVison/test_dianshi_pic/
    """
    # root_imgs = "/home/hanjianhui/Testingcodes/Pytorch_mrcnns/PyTorch-Simple-MaskRCNN-res101/2022_2_24/10.40.15.232_01_20220224090213769.jpeg"
    # root_imgs = "/home/hanjianhui/Testingcodes/Pytorch_mrcnns/Mask-RCNN-pytorchVison/test_dianshi_pic/22_2_18_3_59_295/22_2_18_3_59_295_53750.jpg"
    # root_imgs = "/home/hanjianhui/Testingcodes/Pytorch_mrcnns/PyTorch-Simple-MaskRCNN-res101/2022_2_22/22_2_21_20_49_284/22_2_21_20_49_284_40400.jpg"
    root_imgs = "/home/hanjianhui/Testingcodes/Pytorch_mrcnns/PyTorch-Simple-MaskRCNN-res101/2022_3_11/22_3_10_13_18_288_18400.jpg"

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
        for idx,box in enumerate(boxes):
            xmin=box[0]
            ymin=box[1]
            xmax=box[2]
            ymax=box[3]
            if scores[idx]>0.9:
                cv2.rectangle(image_ori, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color=(0, 255, 0), thickness=3)

                mask = masks[idx,:, :].cpu().detach().numpy()
                print("main_max",np.max(mask),np.min(mask))

                color = (0, 0,150)
                for c in range(3):
                    masked_image[:, :, c] = np.where(mask <0.5,
                                                   masked_image[:, :, c],

                    masked_image[:, :, c] * (1 - 0.5) + 0.5 * color[c])

        cv2.imwrite('tse_crop.jpg', masked_image)

        cv2.imwrite('tse.jpg', image_ori)




#

def imgs():
    #
    """
    /home/hanjianhui/Testingcodes/Pytorch_mrcnns/Mask-RCNN-pytorchVison/test_dianshi_pic/
    /home/hanjianhui/Testingcodes/Pytorch_mrcnns/PyTorch-Simple-MaskRCNN-res101/eval/demo_pcis
    """
    # root_imgs = "/home/hanjianhui/Testingcodes/Pytorch_mrcnns/PyTorch-Simple-MaskRCNN-res101/2022_2_22/22_2_22_4_45_300/22_2_22_4_45_300_7000.jpg"
    # root_imgs = "/home/hanjianhui/Testingcodes/Pytorch_mrcnns/Mask-RCNN-pytorchVison/test_dianshi_pic/22_2_18_3_59_295/22_2_18_3_59_295_53750.jpg"
    root_imgs = "/home/hanjianhui/Testingcodes/Pytorch_mrcnns/PyTorch-Simple-MaskRCNN-res101/eval/demo_pcis/2.jpg"

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


        print(scores)

        image_ori = cv2.cvtColor(np.asarray(image_ori), cv2.COLOR_RGB2BGR)

        masked_image = np.array(image_ori,np.uint8)
        print('masked_image_shape',masked_image.shape)
        # plotted = plot_masks(image_ori, result, classes)
        for idx,box in enumerate(boxes):
            xmin=box[0]
            ymin=box[1]
            xmax=box[2]
            ymax=box[3]
            if scores[idx]>0.9:
                cv2.rectangle(image_ori, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color=(0, 255, 0), thickness=3)

                mask = masks[idx,:, :].cpu().detach().numpy()
                print("main_max",np.max(mask),np.min(mask))

                color = (0, 0,150)
                for c in range(3):
                    masked_image[:, :, c] = np.where(mask <0.15,
                                                   masked_image[:, :, c],

                    masked_image[:, :, c] * (1 - 0.5) + 0.5 * color[c])

        cv2.imwrite('tse_crop102.jpg', masked_image)

        # cv2.imwrite('tse.jpg10', image_ori)




imgs()