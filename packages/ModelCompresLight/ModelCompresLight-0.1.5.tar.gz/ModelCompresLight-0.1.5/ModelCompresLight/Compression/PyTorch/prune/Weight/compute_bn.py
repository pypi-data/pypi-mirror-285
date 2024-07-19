from __future__ import absolute_import
import torch
import os
import numpy as np
import sys


def channels_slit_nb(forward_channels):
    """
    compute layer option nb
    :return:
    """
    if forward_channels <= 16:
        layer_nb = [i for i in range(2, forward_channels + 1, 2)]
        if forward_channels not in layer_nb:
            layer_nb.append(forward_channels)
        return layer_nb

    elif (forward_channels > 16 and forward_channels <= 64):
        layer_nb=[i for i in range(8,forward_channels+1,4)]
        if forward_channels not in layer_nb:
            layer_nb.append(forward_channels)
        return layer_nb


    elif (forward_channels > 64 and forward_channels <= 128):
        layer_nb = [i for i in range(8, forward_channels+1, 8)]
        if forward_channels not in layer_nb:
            layer_nb.append(forward_channels)
        return layer_nb

    elif (forward_channels > 128 and forward_channels <= 256):
        layer_nb = [i for i in range(8, forward_channels+1, 16)]
        if forward_channels not in layer_nb:
            layer_nb.append(forward_channels)
        return layer_nb

    elif (forward_channels > 256 and forward_channels <= 512):
        layer_nb = [i for i in range(8, 513, 32)]
        if forward_channels not in layer_nb:
            layer_nb.append(forward_channels)
        return layer_nb

    else:
        layer_nb = [i for i in range(8, forward_channels+1, 64)]
        if forward_channels not in layer_nb:
            layer_nb.append(forward_channels)
        return layer_nb
def best_channels(nb,ratio):

    channels_=channels_slit_nb(nb)
    keep_nb=int(nb*(1-ratio))
    reduce=np.array(channels_)-keep_nb
    return channels_[np.argsort(np.abs(reduce))[0]]
class Batch_Norm():
    def __init__(self,model,pru_ratio,use_global_bn=True):
        self.net=model
        self.pru_ratio=pru_ratio# pru_ratio means pruned 30% bns
        self.use_global_bn=True
        self.layer_thrs = {}
        if use_global_bn:
            self.Get_BNS()
        else:
            self.Get_bn()


    def get_attr(self,layer):
        layer_name = layer.strip().split('.')[0:-1]  # pop weight

        current_attr = None

        def current_att(attribute, idx):
            return attribute._modules[idx]

        if hasattr(self.net, '_modules'):
            current_attr = self.net
            for attr in layer_name:
                if attr == "module":
                    continue
                if hasattr(current_attr, '_modules'):
                    current_att_ = current_att(current_attr, attr)
                    current_attr = current_att_
        return current_attr

    def Get_bn(self):
        model_dicts = self.net.state_dict()
        BN_layers = []
        all_using_bn = []
        for key, value in model_dicts.items():

            attr_get = self.get_attr(key)
            if (isinstance(attr_get, torch.nn.BatchNorm2d) or isinstance(attr_get,
                                                                         torch.nn.BatchNorm1d)) and 'weight' in key and len(
                    list(value.shape)) == 1:

                prune_nb = value.shape[0] - best_channels(value.shape[0], self.pru_ratio)
                if self.pru_ratio != 0 and prune_nb != 0:

                    layer_thr= torch.sort(value, descending=False)[0][round(value.shape[0] * self.pru_ratio)]
                    indexs=torch.nonzero(value>layer_thr).squeeze().cpu().detach().numpy().tolist()
                    BN_layers.extend(value.cpu().numpy().tolist())
                    all_using_bn.extend(indexs.cpu().numpy().tolist())

                    self.layer_thrs[key]=indexs

                else:
                    indexs = [i for i in range(0,value.shape[0])]

                    BN_layers.extend(value.cpu().numpy().tolist())
                    all_using_bn.extend(indexs)

                    self.layer_thrs[key] = indexs

        print("using every bn to compute threshold,it's ration is :",1-len(all_using_bn)/len(BN_layers))

    def Get_BNS(self):
        BN_layers_th=[]
        all_using_bns=[]
        model_dicts=self.net.state_dict()
        for key,value in model_dicts.items():
            value=torch.abs(value)/torch.max(value)
            attr_get=self.get_attr(key)
            if (isinstance(attr_get,torch.nn.BatchNorm2d) or isinstance(attr_get,torch.nn.BatchNorm1d)) and 'weight' in key and len(list(value.shape))==1:
                BN_layers_th.extend(value.cpu().numpy().tolist())
        BN_layer_tensor=torch.tensor(BN_layers_th,dtype=torch.float32).squeeze()
        sorted = torch.sort(BN_layer_tensor, descending=False)[0]
        all_bn_threshold=sorted[round(len(BN_layers_th) * self.pru_ratio)]


        for k,v in model_dicts.items():

            attr_get_bn=self.get_attr(k)
            if (isinstance(attr_get_bn,torch.nn.BatchNorm2d) or isinstance(attr_get_bn,torch.nn.BatchNorm1d)) and 'weight' in k and len(list(v.shape))==1:
                v=torch.abs(v)/torch.max(v)
                indexs = torch.nonzero(v > all_bn_threshold).squeeze()

                try:
                    lens=indexs.shape[0]
                    if lens<int(v.shape[0]*0.1):
                        print("Threshold is too big<<0.1", k)
                        prune_nb = v.shape[0] - best_channels(v.shape[0], 0.8)

                        layer_thr = torch.sort(v, descending=False)[0][prune_nb-1]
                        indexs = torch.nonzero(v > layer_thr).squeeze()
                        self.layer_thrs[k] = indexs
                        all_using_bns.extend(indexs.cpu().numpy().tolist())

                    else:
                        print("Threshold is ok<<0.1", k)

                        nbs = channels_slit_nb(lens)
                        re_set_index = [e for e in range(0, nbs[-2], 1)]
                        self.layer_thrs[k] = indexs[re_set_index].cpu().numpy().tolist()
                        all_using_bns.extend(indexs[re_set_index].cpu().numpy().tolist())
                except:
                    print("Threshold is too too big",k)
                    layer_thr = torch.sort(v, descending=False)[0][round(v.shape[0] * 0.8)]
                    indexs = torch.nonzero(v > layer_thr).squeeze()
                    self.layer_thrs[k] = indexs
                    all_using_bns.extend(indexs.cpu().numpy().tolist())

        print("using all bns to compute threshold,it's ration is :",1-len(all_using_bns)/len(BN_layers_th))

    def __call__(self,layer):
        return self.layer_thrs[layer]



#
# if __name__ == '__main__':
#     sys.path.insert(0, '/opt/share1/hanjianhui/TestingCode/detect/Vihicle/yolov5-gyj')
#     model = torch.load('/opt/share1/hanjianhui/TestingCode/detect/Vihicle/yolov5-gyj/yolov5.pth', map_location='cpu')
#     data = torch.tensor(np.random.random(size=[1, 3, 960, 960])).to(torch.float32)
#     yamlepth='./yolov5_use.yaml'
#     Batch_Norm_=Batch_Norm(model,pru_ratio=0.3,use_global_bn=True)
#
#     print(Batch_Norm_)
