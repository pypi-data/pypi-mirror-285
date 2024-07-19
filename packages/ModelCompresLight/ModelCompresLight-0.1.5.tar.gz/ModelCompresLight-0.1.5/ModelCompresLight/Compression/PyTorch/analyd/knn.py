# -*- coding: utf-8 -*- #

# ------------------------------------------------------------------
import torch
import cv2
print(torch.cuda.is_available())
from torch.nn import MSELoss
from torch import nn
import torch.nn.functional as F
import torch.utils.data as data
import numpy as np
import os
class LRNET(nn.Module):

    """
    knn---re-struct

    """
    def __init__(self,out_nb):
        super(LRNET,self).__init__()
        self.fc1 = nn.Linear(out_nb, 1024)
        self.fc2 = nn.Linear(1024, 2048)
        self.fc3 = nn.Linear(2048, 256)
        self.fc4= nn.Linear(256, 2)

        # self.out_nb=out_nb
    def forward(self, x):
        x1 = F.relu(self.fc1(x))
        x1 = F.dropout(x1, p=0.5)
        x2 = F.relu(self.fc2(x1))
        x2 = F.dropout(x2, p=0.5)
        x3 = F.relu(self.fc3(x2))
        x3 = F.dropout(x3, p=0.5)

        x4 = self.fc4(x3)

        return x4

class logdata(data.Dataset):
    def __init__(self):
        super(logdata,self).__init__()
        self.train_dat=[]
        self.labels=[]
        self.out_nb = 0
        """
       
        """

        with open("input_csv",'r') as fw:
            lines=fw.readlines()
            for idx,line in enumerate(lines):
                if idx==0:
                    continue
                # elif idx==100:
                #     break
                line_arr=line.split(',')
                tmp=[]
                tmp.append(eval(line_arr[4]))
                self.train_dat.append(tmp)
                self.labels.append(eval(line_arr[-1]))
        self.out_nb=len(self.train_dat[0])
        print(len(self.labels))

    def __getitem__(self, idx):
        input=self.train_dat[idx]
        label=self.labels[idx]
        return np.array(input), np.array(label)

    def __len__(self):
        return len(self.train_dat)

class logdataTest(data.Dataset):
    def __init__(self):
        super(logdataTest,self).__init__()
        self.train_dat=[]
        self.labels=[]

        with open('out.csv','r') as fw:
            lines=fw.readlines()
            for idx,line in enumerate(lines):
                if idx==0:
                    continue
                line_arr = line.split(',')
                tmp = []

                tmp.append(eval(line_arr[4]))
                tmp.append(eval(line_arr[5]))
                tmp.append(eval(line_arr[6]))
                tmp.append(eval(line_arr[7]))

                tmp.append(eval(line_arr[10]))

                self.train_dat.append(tmp)
                self.labels.append(eval(line_arr[-1]))


        print(len(self.labels))


    def __getitem__(self, idx):

        input=self.train_dat[idx]
        label=self.labels[idx]

        return np.array(input), np.array(label)




    def __len__(self):
        return len(self.train_dat)

def TrainLoad():
    """
    load model to fast

        -- load model
        --load datalaoder
        --load datasest
    :return:
    """
    datesets_for_train=logdata()
    datesets_for_test=logdataTest()
    train_loader=data.DataLoader(datesets_for_train, batch_size=32, shuffle=True, num_workers=8, pin_memory=True)
    test_loader=data.DataLoader(datesets_for_test, batch_size=32, shuffle=True, num_workers=8, pin_memory=True)
    model=LRNET(train_loader.out_nb)
    model.cuda()
    optimizer = torch.optim.SGD(model.parameters(), 0.001,
                                        momentum=0.9,
                                        weight_decay=0.0001)

    scheduler_cos = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=150,eta_min=0)
    scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer,milestones=[20,30], gamma=0.2)
    return scheduler_cos,scheduler

def fast_2_run(model,epochs,train_loader,optimizer,scheduler):

    """

    :param model:
    :param epochs:
    :param train_loader:
    :param optimizer:
    :param scheduler:
    :return:  trained_model
    """

    loss_func=torch.nn.CrossEntropyLoss()
    for epoch in range(epochs):

        model.train()
        for i, data in enumerate(train_loader):
            input,label=data[0],data[1]
            inputs = input.cuda()
            classes = label.cuda()
            optimizer.zero_grad()
            inputs = inputs.float()
            classes = classes.float()
            # classes = classes.int().view(cfg['batch_size'], 3)
            reg_out = model(inputs)
            masks = torch.tensor(classes).long()
            # masks__ = torch.permute(masks, [0, 2, 3, 1]).long()
            ont_hot_d = torch.nn.functional.one_hot(masks, 2)
            loss = loss_func(reg_out.float(), ont_hot_d.float())
            loss.backward()
            optimizer.step()

        scheduler.step(epoch)
        # -------------------------------------test//or//train-------------------------------

        correct = 0
        total = 0
        for i, data in enumerate(train_loader):
            input,label=data[0],data[1]
            inputs = input.cuda()
            classes = label.cuda()
            inputs = inputs.float()
            scores = classes.float()
            reg_out = model(inputs)
            _, predicted = torch.max(reg_out, 1)
            total += classes.size(0)
            correct += (predicted == classes).sum().item()

            acc__=correct / total
            # print(f'Accuracy of the network on the 10000 test images: {100 * correct / total}%')

    return model

