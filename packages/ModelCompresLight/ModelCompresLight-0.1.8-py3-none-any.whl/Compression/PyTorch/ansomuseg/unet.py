# -*- coding: utf-8 -*- #
#ai-cop-for Model C
import numpy as np
import os
import csv
import copy
import time
from sklearn.metrics import f1_score
import cv2
import torch
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader
import segmentation_models_pytorch as smp

image_path = "input you images"
mask_path = "input you labels"

class GetData(Dataset):

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

def dataload():
    data_transforms = {
        'Train': transforms.Compose([transforms.ToPILImage(), transforms.Resize((512, 512)), transforms.ToTensor()]),

        'Test': transforms.Compose([transforms.ToPILImage(), transforms.Resize((512, 512)), transforms.ToTensor()]),

    }
    image_datasets = {
        'Train': GetData(image_path, mask_path, transform=data_transforms['Train']),
        'Test': GetData(image_path, mask_path, transform=data_transforms['Test'])
    }
    dataloaders = {x: DataLoader(image_datasets[x], batch_size=16,
                                 shuffle=True, num_workers=8)
                   for x in ['Train', 'Test']}

    return dataloaders, image_datasets

dataloaders, image_datasets = dataload()


model = smp.Unet(
    encoder_name="resnet18",
    encoder_weights=None,
    in_channels=3,
    classes=13,
)


def train_model(model, criterion, dataloaders, optimizer, metrics, bpath, num_epochs=3):
    since = time.time()
    best_model_wts = copy.deepcopy(model.state_dict())
    best_loss = 1e10

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") #xm.xla_device()
    model.to(device)


    for epoch in range(1, num_epochs+1):


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
                    outputs = model(inputs).permute(0,2,3,1)
                    # masks=torch.tensor(masks).long().unsqueeze(-1)
                    masks=torch.tensor(masks).long()
                    ont_hot_d = torch.nn.functional.one_hot(masks, 13)
                    # masks__ = torch.permute(masks, [0, 2, 3, 1]).long()
                    # ont_hot_d=torch.nn.functional.one_hot(masks,13)

                    loss = criterion(outputs, ont_hot_d.float())

                    if phase == 'Train':
                        loss.backward()
                        optimizer.step()

        if phase == 'Test' and loss < best_loss:
            best_loss = loss
            best_model_wts = copy.deepcopy(model.state_dict())
    print(best_loss)

    model.load_state_dict(best_model_wts)
    return model

epochs = 5
bpath = "./outputs/"
os.makedirs(bpath,exist_ok=True)
criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)


metrics = {'f1_score': f1_score} #, 'auroc': roc_auc_score}

trained_model=train_model(model, criterion, dataloaders,optimizer, bpath=bpath, metrics=metrics, num_epochs=epochs)

torch.save(trained_model, os.path.join(bpath, f'{epochs}_model.pt'))




