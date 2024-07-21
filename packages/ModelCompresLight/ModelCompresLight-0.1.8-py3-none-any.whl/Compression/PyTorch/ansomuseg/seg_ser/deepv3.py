# -*- coding: utf-8 -*- #

import os
from torchvision.models.segmentation.deeplabv3 import DeepLabHead
import cv2
from torchvision import models
import torch
from torchvision import transforms, utils
from torch.utils.data import Dataset, DataLoader
import segmentation_models_pytorch as smp
from torchvision import models
from torchvision.models.segmentation.deeplabv3 import DeepLabHead

def createDeepLabv3(outputchannels=1):
    model = models.segmentation.deeplabv3_resnet50(
        pretrained=True, progress=True)
    model.classifier = DeepLabHead(2048, outputchannels)
    model.train()
    return model

image_path = "images"
mask_path = "labels"

class Loadataset(Dataset):

    def __init__(self, img_dirs, mask_dirs, transform=None):
        self.img_dir = img_dirs
        self.mask_dir = mask_dirs
        self.transform = transform
        self.image_names = []
        self.mask_names = []
        if type(self.img_dir) == list:
            for i, j in zip(img_dirs, mask_dirs):
                for n in os.listdir(i):
                    self.image_names.append(os.path.join(i, n))
                    self.mask_names.append(os.path.join(j, n))
        else:
            for n in os.listdir(self.img_dir):
                self.image_names.append(os.path.join(self.img_dir, n))
                self.mask_names.append(os.path.join(self.mask_dir, n))

    def __len__(self):
        return len(self.image_names)

    def __getitem__(self, idx):
        img_name = self.image_names[idx]
        image = cv2.imread(img_name)
        mask_name = self.mask_names[idx]
        mask = cv2.imread(mask_name)[:,:,2]

        sample = {'image': image, 'mask': mask}

        if self.transform:
            sample['image'] = self.transform(sample['image'])
        # cv2.INTER_LINEAR：INTER_NEAREST INTER_LINEAR
        sample['mask'] =cv2.resize(mask,(512,512),interpolation=cv2.INTER_NEAREST)

        return sample


train_transformer=transforms.Compose([transforms.ToPILImage(), transforms.Resize((512, 512)), transforms.ToTensor()])

test_transformer=transforms.Compose([transforms.ToPILImage(), transforms.Resize((512, 512)), transforms.ToTensor()])
train_datasets=Loadataset(image_path, mask_path, transform=train_transformer)

train_data_loder=DataLoader(train_datasets,batch_size=4,shuffle=True, num_workers=8)

model = createDeepLabv3(13)

num_epochs=10
device = torch.device("cuda:0" )
model.to(device)
criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)


for epoch in range(1, num_epochs+1):
    model.train()   # Set model to evaluate mode
    for sample in train_data_loder:
        inputs_img = sample['image'].to(device)
        masks = sample['mask'].to(device)
        print("mask_has_value", torch.unique(masks))
        optimizer.zero_grad()
        #model(inputs)['out']
        outputs = model(inputs_img)['out'].permute(0,2,3,1)
        # masks=torch.tensor(masks).long().unsqueeze(-1)
        masks=torch.tensor(masks).long()
        ont_hot_d = torch.nn.functional.one_hot(masks, 13)
        loss = criterion(outputs, ont_hot_d.float())
        loss.backward()
        optimizer.step()
    torch.save(model,os.path.join('./weights',f'{epoch}_best.pt'))



