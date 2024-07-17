# -*- coding: utf-8 -*- #

import pandas as pd
import numpy as np
import os
import random

# import matplotlib.pyplot as plt

import cv2
# from PIL import Image

import torch
from torchvision import transforms, utils
from torch.utils.data import Dataset, DataLoader


image_path = "images"
mask_path = "gts"


class SDCDataset(Dataset):
    '''
    For collectively storing the images and the masks
    '''

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
        sample['mask'] =cv2.resize(mask,(800,600),interpolation=cv2.INTER_NEAREST)

        # print("mask_has_value111", np.unique(sample['mask'] ))
        # print("mask_has_value113", np.unique(mask ))

        return sample


# class Normalize(object):
#     '''Normalize image'''

#     def __call__(self, sample):
#         image, mask = sample['image'], sample['mask']
#         return {'image':image.type(torch.FloatTensor)/255, 'mask':mask.type(torch.FloatTensor)/255}

def dataload():
    data_transforms = {
        'Train': transforms.Compose([transforms.ToPILImage(), transforms.Resize((600, 800)), transforms.ToTensor()]),
        # Resize((256, 256), (256, 256)),
        'Test': transforms.Compose([transforms.ToPILImage(), transforms.Resize((600, 800)), transforms.ToTensor()]),
        # Resize((256, 256), (256, 256))
    }
    image_datasets = {
        'Train': SDCDataset(image_path, mask_path, transform=data_transforms['Train']),
        'Test': SDCDataset(image_path, mask_path, transform=data_transforms['Test'])
    }
    dataloaders = {x: DataLoader(image_datasets[x], batch_size=4,
                                 shuffle=True, num_workers=8)
                   for x in ['Train', 'Test']}

    return dataloaders, image_datasets

dataloaders, image_datasets = dataload()

from torchvision import models
from torchvision.models.segmentation.deeplabv3 import DeepLabHead
# from torchvision.models.seimport DeepLabHead


def createDeepLabv3(outputchannels=1):
    model = models.segmentation.deeplabv3_resnet50(
        pretrained=True, progress=True)
    # Added a Tanh activation after the last convolution layer
    model.classifier = DeepLabHead(2048, outputchannels)
    # Set the model in training mode
    model.train()
    return model


model = createDeepLabv3(13)


import csv
import copy
import time
from tqdm.notebook import tqdm
from sklearn.metrics import f1_score, roc_auc_score

import torch.nn.functional as F

def multi_classes_dice_loss(preds, targets, num_classes):
    dice_loss = 0
    for cls in range(num_classes):
        pred = preds[:, :,cls]
        target = targets[:, :,cls]
        intersection = (pred * target).sum()
        union = pred.sum() + target.sum()
        dice_loss += 1 - ((2 * intersection + 1e-5) / (union + 1e-5))
    return dice_loss / num_classes

def train_model(model, criterion, dataloaders, optimizer, metrics, bpath, num_epochs=3):
    since = time.time()
    best_model_wts = copy.deepcopy(model.state_dict())
    best_loss = 1e10
    # Use gpu if available
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") #xm.xla_device()
    model.to(device)
    # Initialize the log file for training and testing loss and metrics
    fieldnames = ['epoch', 'Train_loss', 'Test_loss'] + \
        [f'Train_{m}' for m in metrics.keys()] + \
        [f'Test_{m}' for m in metrics.keys()]
    os.makedirs(bpath,exist_ok=True)
    with open(os.path.join(bpath, 'log.csv'), 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    for epoch in range(1, num_epochs+1):
        print('Epoch {}/{}'.format(epoch, num_epochs))
        print('-' * 10)
        # Each epoch has a training and validation phase
        # Initialize batch summary
        batchsummary = {a: [0] for a in fieldnames}

        for phase in ['Train', 'Test']:
            if phase == 'Train':
                model.train()  # Set model to training mode
            else:
                model.eval()   # Set model to evaluate mode

            # Iterate over data.
            for sample in iter(dataloaders[phase]):
                inputs = sample['image'].to(device)
                masks = sample['mask'].to(device)
                print("mask_has_value", torch.unique(masks))
                # zero the parameter gradients
                optimizer.zero_grad()

                # track history if only in train
                with torch.set_grad_enabled(phase == 'Train'):
                    outputs = model(inputs)['out'].permute(0,2,3,1)
                    masks=torch.tensor(masks).long()
                    # masks__ = torch.permute(masks, [0, 2, 3, 1]).long()

                    ont_hot_d=torch.nn.functional.one_hot(masks,13)

                    # masks__
                    loss = criterion(outputs, ont_hot_d.float())
                    # y_pred = outputs['out'].data.cpu().numpy().ravel()
                    # y_true = masks.data.cpu().numpy().ravel()
#                     print(y_pred, y_true)
#                     for name, metric in metrics.items():
#                         if name == 'f1_score':
#                             # Use a classification threshold of 0.1
#                             batchsummary[f'{phase}_{name}'].append(
#                                 metric(y_true > 0, y_pred > 0.01))
#                         else:
#                             batchsummary[f'{phase}_{name}'].append(
#                                 metric(y_true.astype('uint8'), y_pred))

                    # backward + optimize only if in training phase
                    if phase == 'Train':
                        loss.backward()
                        optimizer.step()
            batchsummary['epoch'] = epoch
            epoch_loss = loss
            batchsummary[f'{phase}_loss'] = epoch_loss.item()
            print('{} Loss: {:.4f}'.format(
                phase, loss))
        for field in fieldnames[3:]:
            batchsummary[field] = np.mean(batchsummary[field])
        print(batchsummary)
        with open(os.path.join(bpath, 'log.csv'), 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow(batchsummary)
            # deep copy the model
            if phase == 'Test' and loss < best_loss:
                best_loss = loss
                best_model_wts = copy.deepcopy(model.state_dict())

    time_elapsed = time.time() - since
    print('Training complete in {:.0f}m {:.0f}s'.format(
        time_elapsed // 60, time_elapsed % 60))
    print('Lowest Loss: {:4f}'.format(best_loss))

    # load best model weights
    model.load_state_dict(best_model_wts)
#     torch.save(model, os.path.join(bpath, '50epochs_weights.pt'))
    return model

epochs = 15
bpath = "./working_v3/"

# Specify the loss function
criterion = torch.nn.CrossEntropyLoss()
# Specify the optimizer with a lower learning rate
optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)

# Specify the evalutation metrics
metrics = {'f1_score': f1_score} #, 'auroc': roc_auc_score}

trained_model=train_model(model, criterion, dataloaders,optimizer, bpath=bpath, metrics=metrics, num_epochs=epochs)
# xmp.spawn(train_model, args=(model, criterion, dataloaders, optimizer, bpath=bpath, metrics=metrics, num_epochs=num_epochs))

torch.save(trained_model, os.path.join(bpath, f'{epochs}_deeplabv3_torch_resnet50_.pt'))




