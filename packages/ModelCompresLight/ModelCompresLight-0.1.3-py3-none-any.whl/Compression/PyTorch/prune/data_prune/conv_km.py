from __future__ import absolute_import
import torch
import numpy as np
import copy
from sklearn.cluster import KMeans



class L2Kmeans():
    def __init__(self,model,config):
        self.model=model
        self.config=config
        self.layers_config=dict()
        self.end_layers_config={}
        if self.config['evaluate']=='loss':
            self.evaluate='loss'
        elif  self.config['evaluate']=='map':
            self.evaluate='acc'
        elif  self.config['evaluate']=='acc':
            self.evaluate='acc'



    def recomend(self,x, y,loss_acc='loss'):
        grad_list = []
        grad_x_row = []
        for i, e in enumerate(x):
            if i < len(x) - 1:
                if loss_acc=='loss':
                    grads = (y[i] - y[i + 1]) / (x[i + 1] - x[i])
                elif loss_acc=='acc':
                    grads = (y[i+1] - y[i]) / (x[i + 1] - x[i])

                grad_x_row.append((x[1] - x[0]) * (i + 1))
                grad_list.append(grads)  # use acc:  add -     use acc: del -
                # print(grad)
        arg = np.argsort(grad_list) + 1  # [ 1  3  4  5  2  7  9 10  6 13 15  8 11 12 14]
        reverse = []  #
        id = len(arg) - 1

        for i, e in enumerate(arg):
            if id >= 0:
                reverse.append(arg.tolist()[id])
                id -= 1
        final_sort = []  # [1, 3, 4, 5, 7, 9, 10, 13, 15]
        max_v = 0
        for i in range(len(reverse)):
            if reverse[i] > max_v:
                max_v = reverse[i]
                final_sort.append(reverse[i])
        half = int(len(final_sort))  # [1, 3, 4, 5, 7, 9, 10, 13, 15]
        id = final_sort[0:half]  # [ 48 112 144 176]
        return id

    def compute_end_nb(self):

        ### select form layer_nb_acc
        for k, v in self.layers_config.items():
            #v:[(nb,index,loss),...]
            nb_list_ = []
            acc_loss_list = []
            index_list=[]
            for e in v:
                nb_list_.append(e[0])
                index_list.append(e[1])

                acc_loss_list.append(e[2])


            recomend_id = self.recomend(nb_list_, acc_loss_list, self.evaluate)
            if len(recomend_id)>=1:
                pass
            else:
                recomend_id=[len(nb_list_)-1]


            recommend_nb_list = np.array(nb_list_)[recomend_id].tolist()
            recommend_acc_loss_list = np.array(acc_loss_list)[recomend_id].tolist()
            recommend_index_list = np.array(index_list)[recomend_id].tolist()


            self.end_layers_config[k]= {'nbs_list':recommend_nb_list,'index_list':recommend_index_list,'value':recommend_acc_loss_list}



    def set0_nb_layer_(self, main_layer:str,nb:int):
        copy_model=copy.deepcopy(self.model)
        for param in copy_model.parameters():
            param.requires_grad = False
        current_layer=copy_model.state_dict()[main_layer]

        KM = KMeans(n_clusters=nb, n_jobs=10)
        weight = current_layer.data.numpy()
        KM.fit(np.reshape(weight, newshape=[weight.shape[0], -1]))

        lebels = KM.labels_
        lebel_dealed = []
        nb_list_j = [] #keeped channels

        for j, e_ls in enumerate(lebels):
            if e_ls in lebel_dealed:


                copy_model.state_dict()[main_layer][j,...] = 0

            else:
                nb_list_j.append(j)
                lebel_dealed.append(e_ls)

        return copy_model,nb_list_j



