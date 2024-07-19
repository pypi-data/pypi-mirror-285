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
class ComputeConv():
    def __init__(self,model,pru_ratio,use_global_bn=True):
        self.net=model
        self.pru_ratio=pru_ratio# pru_ratio means pruned 30% bns
        self.use_global_bn=True
        self.layer_thrs = {}
        if use_global_bn:
            self.Get_convs()
        else:
            self.Get_conv()


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

    def Get_conv(self):
        model_dicts = self.net.state_dict()
        BN_layers = []
        all_using_bn = []
        for key, value in model_dicts.items():

            attr_get = self.get_attr(key)
            if (isinstance(attr_get, torch.nn.Conv2d) or isinstance(attr_get,torch.nn.Conv1d)) and 'weight' in key and len(
                    list(value.shape)) >= 4:

                value=  torch.sum(value,dim=[1,2,3])

                value=torch.abs(value)
                prune_nb = value.shape[0] - best_channels(value.shape[0], self.pru_ratio)
                if self.pru_ratio!=0 and prune_nb !=0:


                    layer_thr= torch.sort(value, descending=False)[0][prune_nb-1]
                    # indexs=torch.nonzero(value>layer_thr).squeeze()

                    indexs=torch.nonzero(value>layer_thr).squeeze().cpu().detach().numpy().tolist()

                    BN_layers.extend(value.cpu().numpy().tolist())
                    all_using_bn.extend(indexs)

                    self.layer_thrs[key]=indexs
                else:
                    # layer_thr= -np.inf
                    # indexs = torch.nonzero(value > layer_thr).squeeze().cpu().detach().numpy().tolist()
                    indexs= [i for i in range(0,value.shape[0])]

                    BN_layers.extend(value.cpu().numpy().tolist())
                    all_using_bn.extend(indexs)

                    self.layer_thrs[key] = indexs



        # print("using every bn to compute threshold,it's ration is :",1-len(all_using_bn)/len(BN_layers) if len(all_using_bn)>1 else '')
        print("using every bn to compute threshold,it's ration is :",1-len(all_using_bn)/len(BN_layers))

    def Get_convs(self):
        BN_layers_th=[]
        all_using_bns=[]
        model_dicts=self.net.state_dict()
        for key,value in model_dicts.items():


            attr_get=self.get_attr(key)
            if (isinstance(attr_get,torch.nn.Conv2d) or isinstance(attr_get,torch.nn.Conv1d)) and 'weight' in key and len(list(value.shape))>=3:
                # value = torch.abs(value)/torch.max(value)
                value = torch.abs(value)

                value = torch.sum(value, dim=[1, 2, 3])

                BN_layers_th.extend(value.cpu().numpy().tolist())


        BN_layer_tensor=torch.tensor(BN_layers_th,dtype=torch.float32).squeeze()
        sorted = torch.sort(BN_layer_tensor, descending=False)[0]
        all_conv_threshold=sorted[round(len(BN_layers_th) * self.pru_ratio)]


        for k,value in model_dicts.items():

            attr_get_bn=self.get_attr(k)
            if (isinstance(attr_get_bn,torch.nn.Conv2d) or isinstance(attr_get_bn,torch.nn.Conv1d)) and 'weight' in k and len(list(value.shape))>=3:
                # value = torch.abs(value)/ torch.max(value)
                value = torch.abs(value)

                value = torch.sum(value, dim=[1, 2, 3])

                if self.pru_ratio!=0:

                    indexs = torch.nonzero(value > all_conv_threshold).squeeze()

                    try:
                        lens=indexs.shape[0]
                        if lens<int(value.shape[0]*0.1):
                            print("Threshold is too big<<0.1", k)
                            prune_nb = value.shape[0] - best_channels(value.shape[0], 0.8)

                            layer_thr = torch.sort(value, descending=False)[0][prune_nb-1]
                            indexs = torch.nonzero(value > layer_thr).squeeze().cpu().numpy().tolist()
                            self.layer_thrs[k] = indexs
                            all_using_bns.extend(indexs)

                        else:
                            print("Threshold is ok<<0.1", k)

                            nbs = channels_slit_nb(lens)
                            re_set_index = [e for e in range(0, nbs[-2], 1)]
                            self.layer_thrs[k] = indexs[re_set_index].cpu().numpy().tolist()
                            all_using_bns.extend(indexs[re_set_index].cpu().numpy().tolist())


                    except:
                        print("Threshold is too too big",k)
                        prune_nb = value.shape[0] - best_channels(value.shape[0], 0.8)

                        layer_thr = torch.sort(value, descending=False)[0][prune_nb-1]
                        indexs = torch.nonzero(value > layer_thr).squeeze().cpu().numpy().tolist()
                        self.layer_thrs[k] = indexs
                        all_using_bns.extend(indexs)
                else:
                    indexs= [i for i in range(0,value.shape[0])]
                    self.layer_thrs[k] = indexs
                    all_using_bns.extend(indexs)


        print("using all bns to compute threshold,it's ration is :",1-len(all_using_bns)/len(BN_layers_th))

    def __call__(self,layer):
        return self.layer_thrs[layer]

class Compute_conv_fpgm():
    def __init__(self,model,pru_ratio,use_global_bn=True):
        self.net=model
        self.pru_ratio=pru_ratio# pru_ratio means pruned 30% bns
        self.use_global_bn=True
        self.layer_thrs = {}
        if use_global_bn:
            self.Get_fpgm_conv()
        else:
            self.Get_fpgm_conv()


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


    def get_index(self, weight, num_prune):
        min_gm_idx = self._get_min_gm_kernel_idx(weight, num_prune)
        return min_gm_idx

    def _get_min_gm_kernel_idx(self, weight, n):

        dist_list = []
        for out_i in range(weight.shape[0]):
            dist_sum = self._get_distance_sum(weight, out_i)
            dist_list.append((dist_sum, out_i))
        min_gm_kernels = sorted(dist_list, key=lambda x: x[0])[:n]
        return [x[1] for x in min_gm_kernels]


    def _get_distance_sum(self, weight, out_idx):
        """
        Calculate the total distance between a specified filter (by out_idex and in_idx) and
        all other filters.
        Parameters
        ----------
        weight: Tensor
            convolutional filter weight
        out_idx: int
            output channel index of specified filter, this method calculates the total distance
            between this specified filter and all other filters.
        Returns
        -------
        float32
            The total distance
        """
        # w = weight.view(weight.size(0), -1)
        # anchor_w = w[out_idx].unsqueeze(0).expand(w.size(0), w.size(1))
        # x = w - anchor_w
        # x = (x * x).sum(-1)
        # x = torch.sqrt(x)
        # return x.sum()


        # assert len(weight.shape) in [3, 4], 'unsupported weight shape'
        w = weight.reshape(weight.shape[0], -1)
        anchor_w = w[out_idx].unsqueeze(0).expand(w.size(0), w.size(1))
        x = w - anchor_w
        x = (x * x).sum(-1)
        x = np.sqrt(x)
        return x.sum()



    def Get_fpgm_conv(self):
        model_dicts = self.net.state_dict()
        BN_layers = []
        all_using_bn = []
        for key, value in model_dicts.items():

            attr_get = self.get_attr(key)
            if (isinstance(attr_get, torch.nn.Conv2d) or isinstance(attr_get,torch.nn.Conv1d)) and 'weight' in key and len(
                    list(value.shape)) >= 4:


                if self.pru_ratio!=0:


                    prune_nb = value.shape[0] - best_channels(value.shape[0], self.pru_ratio)

                    indexs = self.get_index(value, prune_nb)

                    self.layer_thrs[key] = list(set([i for i in range(value.shape[0])]).difference(set(indexs)))
                else:

                    self.layer_thrs[key] = [i for i in range(value.shape[0])]







#
# if __name__ == '__main__':
#     sys.path.insert(0, '/opt/share1/hanjianhui/TestingCode/detect/Vihicle/yolov5-gyj')
#     model = torch.load('/opt/share1/hanjianhui/TestingCode/detect/Vihicle/yolov5-gyj/yolov5.pth', map_location='cpu')
#     data = torch.tensor(np.random.random(size=[1, 3, 960, 960])).to(torch.float32)
#     yamlepth='./yolov5_use.yaml'
#     Batch_Norm_=ComputeBn_L1Norm(model,pru_ratio=0.5,use_global_bn=True)
#
#     print(Batch_Norm_)
