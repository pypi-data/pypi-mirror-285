from __future__ import absolute_import
import torch
import sys
import numpy as np
import yaml
from Compression.PyTorch.prune.data_prune.conv_km import L2Kmeans
from Compression.PyTorch.prune.Weight.compute_conv import channels_slit_nb
class ComputeDependency(L2Kmeans):
    def __init__(self,model,config):
        super(ComputeDependency,self).__init__(model,config)
        self.current_layer=None
        self.nb=None
        self.current_index=None
        self.tmp_iters=[]
        self.stop=False

    def pop_sub(self,layer_name,nb):

        sub_model,keeped_index=self.set0_nb_layer_(layer_name,nb)
        self.current_layer=layer_name
        self.nb=nb
        self.current_index=keeped_index
        self.stop=False
        for param in sub_model.parameters():
            param.requires_grad = True
        return sub_model

    def pop_layers_nbs(self):
        self.conv2d=[]
        for key,weight in self.model.state_dict().items():
            if len(weight.shape)==4:
                self.conv2d.append((key,channels_slit_nb(weight.shape[0])))
            # len(self.model.state_dict()['model.24.anchor_grid'].shape)
        return self.conv2d
    def start_collect(self,acc_loss,collect_nb=200):


        if len(self.tmp_iters)<=collect_nb:
            self.tmp_iters.append(acc_loss)
        if len(self.tmp_iters)>=collect_nb:
            ave=np.average(np.array(self.tmp_iters))
            if self.current_layer in self.layers_config.keys():

                self.layers_config[self.current_layer].append((self.nb,self.current_index,ave))
            else:
                self.layers_config[self.current_layer]=[(self.nb,self.current_index,ave)]
            self.tmp_iters=[]
            self.stop_collect(True)


    def stop_collect(self,break_flag):
        self.stop=break_flag
        self.stop_collect_model=self.model


    def save_config(self):
        layer_config = {}
        # self.end_layers_config[k]= {'nbs_list':recommend_nb_list,'index_list':recommend_index_list}
        self.original_evaluate=0


        for key,value in self.end_layers_config.items():
            self.original_evaluate=value['value'][-1]
            best_idx=None
            if self.evaluate == 'acc':
                self.best_value = self.original_evaluate * (1 - self.config['decay_ratio'])
                best_idx = np.array(value['value']) > self.best_value

            elif self.evaluate == 'loss':
                self.best_value = self.original_evaluate * (1 + self.config['decay_ratio'])
                best_idx=np.array(value['value'])<self.best_value

            else:
                raise NotImplementedError('must in [acc,loss,map ]')


            layer_config[key]={'nbs_list':np.array([e for e in value['nbs_list']])[best_idx].tolist() ,
                               'index_list':np.array([e for e in value['index_list']])[best_idx].tolist() ,
                                'value':np.array([e for e in value['value']])[best_idx].tolist()
                               }

        with open(self.config['recommend_layers_config'], "w") as f:
            yaml.safe_dump(layer_config, f, encoding='utf-8', allow_unicode=True)


#
# if __name__ == "__main__":
#     config={
#
#         'layer_config':'/opt/share1/hanjianhui/syccode/PytorchModelCompression/graph/pytorch_graph/yolov5_use.yaml',
#         'prune_ration': 0.1,
#         'decay_ratio':10,
#         'global':True,
#         'save_pth':'../../tmp',
#         'evaluate':'loss',
#         'recommend_layers_config':'./recommend.yaml'
#
#     }
#     sys.path.insert(0, '/opt/share1/hanjianhui/TestingCode/detect/Vihicle/yolov5-gyj')
#     model = torch.load('/opt/share1/hanjianhui/TestingCode/detect/Vihicle/yolov5-gyj/yolov5.pth', map_location='cpu')
#
#     recommend_dep = ComputeDependency(model, config)
#
#     for layer in recommend_dep.pop_layers_nbs():
#         layer_name=layer[0]
#         layer_lists=layer[1]
#         for nb in layer_lists:
#             sub_model=recommend_dep.pop_sub(layer_name,nb)
#             for i in range(1000):#---->for imgaes in images
#                 recommend_dep.start_collect(np.random.random(size=[1])[0],200)#------>loss.backward()
#                 if recommend_dep.stop:
#                     model=recommend_dep.stop_collect_model
#                     break
#
#         recommend_dep.compute_end_nb()
#         recommend_dep.save_config()
#
#
#     print(recommend_dep.layers_config)
