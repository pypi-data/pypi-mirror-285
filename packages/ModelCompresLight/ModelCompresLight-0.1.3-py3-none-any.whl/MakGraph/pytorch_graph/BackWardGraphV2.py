from __future__ import absolute_import

import torch

import sys
import numpy as np
from torchviz import make_dot
from torch.autograd import Variable
from collections import OrderedDict
import yaml
class node:
    def __init__(self, layer_name, ops_name, top, bottom, out_number=None,group_number=0):
        """
        group_number==0   -------> bn /scale ...
        group_number==1   -------> convolution and  no group ...
        group_number>1   -------> group convolution depth wise ...

        """
        self.layer_name = layer_name
        self.ops_name = ops_name
        self.top = top
        self.bottom = bottom
        self.out_number=out_number
        self.group_number = group_number


class Connected:
    def __init__(self, id,bottom,ops=None,para_name=None,shape=None):
        """
        group_number==0   -------> bn /scale ...
        group_number==1   -------> convolution and  no group ...
        group_number>1   -------> group convolution depth wise ...

        """
        self.id = id
        self.bottom = bottom
        self.ops = ops
        self.para_name=para_name
        self.shape=shape


class TreeNode:
    def __init__(self,item):
        self.nodes = item  # 构建字典
        self.next = None
        self.pre=None


class Dlink():
    def __init__(self,head:str):
        """
        head--op1--op2--conv
               |
          cov--op3




        :param head:
        """
        self.haed=head



class DotMaker():

    def __init__(self,model,x,path):
        self.model=model

        self.x=x
        self.yaml_pth=path
        self.Nodes=OrderedDict()
        self.outs=self.WarpTorhcOut()
        self.MakeConnect(self.outs, dict(self.model.named_parameters()))
        # print("parameters",[(k,v.shape) for k,v in dict(self.model.named_parameters()).items()])
        self.MakeGraphAndSave()

    def ShowGarph(self):
        self.vis_graph = make_dot(self.outs, params=dict(self.model.named_parameters()))
        self.vis_graph.view()




    def WarpTorhcOut(self):
        out = self.model(self.x)
        new_list = []
        if isinstance(out, dict):
            for k, v in out.items():
                if isinstance(v, list):
                    for one in v:
                        if "grad_fn" in str(one):
                            new_list.append(one)
                else:
                    if "grad_fn" in str(v):
                        new_list.append(k)
        elif isinstance(out, tuple):
            for e in out:
                if isinstance(e, list):
                    for one in e:
                        if "grad_fn" in str(one):
                            new_list.append(one)
                else:
                    if "grad_fn" in str(e):
                        new_list.append(e)
        else:
            new_list.append(out)
        totuple=tuple(new_list)

        # self.vis_graph = make_dot(totuple, params=dict(self.model.named_parameters()))
        # self.graph = self.vis_graph.body
        # self.vis_graph.view()
        return totuple

    def MakeConnect(self,var, params=None):


        if params is not None:
            assert all(isinstance(p, Variable) for p in params.values())
            param_map = {id(v): k for k, v in params.items()}

        seen = set()

        output_nodes = (var.grad_fn,) if not isinstance(var, tuple) else tuple(v.grad_fn for v in var)
        print("output_nodes", output_nodes)
        #{k:id(v) for k, v in params.items()}['model.2.cv2.weight']
        def add_nodes(var):
            if var not in seen:

                if hasattr(var, 'variable'):
                    u = var.variable
                    name = param_map[id(u)] if params is not None else ''

                    if str(id(var)) in self.Nodes.keys():
                        self.Nodes[str(id(var))].bottom.append(str(id(u[0])))
                    else:
                        self.Nodes[str(id(var))] = Connected(id=str(id(var)), bottom=[],
                                                             ops=str(type(var).__name__),para_name=name,shape=list(u.shape))

                seen.add(var)
                if hasattr(var, 'next_functions'):
                    for u in var.next_functions:
                        if u[0] is not None:
                            if str(id(var)) in self.Nodes.keys():
                                self.Nodes[str(id(var))].bottom.append(str(id(u[0])))
                            else:
                                self.Nodes[str(id(var))]=Connected(id=str(id(var)),bottom= [str(id(u[0]))],ops=str(type(var).__name__))

                            add_nodes(u[0])

        # handle multiple outputs
        if isinstance(var, tuple):
            for v in var:
                add_nodes(v.grad_fn)
        else:
            add_nodes(var.grad_fn)


    def find_start_op(self,para_name):
        """
                    --- model.2.m.0.cv1.conv.weight
        :param para:
        :return:
        """
        for key in self.Nodes.keys():
            if self.Nodes[key].para_name==para_name:
                print(self.Nodes[key])
                sta_id=self.Nodes[key].id
                return sta_id

    def find_layer_bottom(self,idx):
        """
        find layer's bottom is

        :return:
        """
        ids=[]
        for key in self.Nodes.keys():
            bottom=self.Nodes[key].bottom
            if idx in bottom:
                ids.append(key)

        return ids

    def find_layer_next(self,idx):
        """
                find layer's next functions is XXX

                :return:
        """

        return self.Nodes[idx].bottom



    def OpPath2Conv(self,para_name):
        """

        :param para_name: model.4.m.0.cv1.conv.bias
        :return:
        """
        main_ops = set()
        slave_ops = set()
        forward_ops = set()
        deal_layer = []  # .add
        sta_id = self.find_start_op(para_name)  #

        sta_bottom = self.find_layer_bottom(sta_id)
        sta_conv_id = None
        PathsToConv={}
        PathsToConvOps=[]



        for str_bot in sta_bottom:
            if self.Nodes[str_bot].ops in ['ThnnConv2DBackward', 'MkldnnConvolutionBackward']:
                sta_conv_id = str_bot
            else:
                print(self.Nodes[str_bot].shape)
        dyn_layer_ids=[]
        dyn_layer_ids.append(sta_conv_id)

        # NodeDict=TreeNode()
        # def template(idx):
        #     find_bottom_is = self.find_layer_bottom(idx)
        #     NodeDict.insert()






        while len(dyn_layer_ids)>=1:
            print('dyn_layer_ids',dyn_layer_ids)
            if dyn_layer_ids[0]==None:
                print('NoneNone',dyn_layer_ids)
                break

            if dyn_layer_ids[0] not in deal_layer:

                if dyn_layer_ids[0]==sta_conv_id:
                    layer_s_bottom = []
                    find_bottom_is=self.find_layer_bottom(dyn_layer_ids[0])
                else:
                    layer_s_bottom = self.find_layer_next(dyn_layer_ids[0])
                    find_bottom_is = self.find_layer_bottom(dyn_layer_ids[0])
                PathsToConvOps.append(self.Nodes[dyn_layer_ids[0]])
                PathsToConv[dyn_layer_ids[0]] = {'para':self.op2para(dyn_layer_ids[0]), 'ops':self.Nodes[dyn_layer_ids[0]],
                                                 'layer_s_bottom':{e_id:(self.op2para(e_id),self.Nodes[e_id]) for e_id in layer_s_bottom},
                                                 'find_bottom_is': {e_id: (self.op2para(e_id), self.Nodes[e_id]) for
                                                                    e_id in find_bottom_is}

                                                 }

                if len(find_bottom_is) >= 1:
                    # down-----self.Nodes[sta_conv_id] self.op2para(e_fw)  self.Nodes[dyn_layer_ids[0]]
                    for e_fw in find_bottom_is:
                        if self.Nodes[e_fw].ops in ['ThnnConv2DBackward', 'MkldnnConvolutionBackward']:
                            forward_ops.add(self.Nodes[e_fw])
                        elif self.Nodes[e_fw].ops in ['NativeBatchNormBackward']:
                            forward_ops.add(self.Nodes[e_fw])
                            if e_fw not in deal_layer:
                                dyn_layer_ids.append(e_fw)
                        elif self.Nodes[e_fw].ops in ['AddBackward0', 'AddBackward']:

                            dyn_layer_ids.append(e_fw)

                        elif self.Nodes[e_fw].ops in ['CatBackward']:

                            dyn_layer_ids.append(e_fw)

                        else:
                            if e_fw not in deal_layer:

                                dyn_layer_ids.append(e_fw)

                if len(layer_s_bottom) >= 1:
                    # up -----|||||
                    for e_up in layer_s_bottom:
                        if self.Nodes[e_up].ops in ['ThnnConv2DBackward', 'MkldnnConvolutionBackward']:
                            slave_ops.add(self.Nodes[e_up])
                        elif self.Nodes[e_up].ops in ['NativeBatchNormBackward']:
                            slave_ops.add(self.Nodes[e_up])
                            if e_up not in deal_layer:
                                dyn_layer_ids.append(e_up)

                        elif self.Nodes[e_up].ops in ['AddBackward0']:

                            dyn_layer_ids.append(e_up)

                        elif self.Nodes[e_up].ops in ['CatBackward']:
                            dyn_layer_ids.append(e_up)

                        else:
                            if e_up not in deal_layer:

                                dyn_layer_ids.append(e_up)
            deal_layer.append(dyn_layer_ids[0])

            dyn_layer_ids.remove(dyn_layer_ids[0])

        op_flag='normal'
        if 'AddBackward0' in PathsToConvOps or 'AddBackward' in PathsToConvOps:
            op_flag='add'
        elif 'CatBackward' in PathsToConvOps or 'CatBackward0' in PathsToConvOps:
            op_flag='concat'

        if sta_conv_id!=None:
            main_ops.add(self.Nodes[sta_conv_id])


            main_para_name=self.wrapout([self.op2para(e.id) for e in main_ops])
            slave_para_name=self.wrapout([self.op2para(e.id) for e in slave_ops])
            slave_para_name=list(set(main_para_name).difference(set(slave_para_name)))

            forward_para_name=self.wrapout([self.op2para(e.id) for e in forward_ops])
            print("main_ops", main_para_name)
            print("slave_ops",slave_para_name )
            print("forward_ops", forward_para_name)


            return main_para_name,slave_para_name,forward_para_name,op_flag
        else:
            return None,None,None,op_flag

    def wrapout(self,weights):
        wraped=[]
        if len(weights)>=1:
            for e in weights:
                if isinstance(e,list):
                    wraped.extend(e)
                else:
                    wraped.append(e)

        return   wraped



    def op2para(self,op_id):
        parameters=[]
        if len(self.Nodes[op_id].bottom)>=1:
            for bot in self.Nodes[op_id].bottom:
                if self.Nodes[bot].shape is not None:
                    parameters.append(self.Nodes[bot].para_name)


        return list(set(parameters))



    def MakeGraphAndSave(self):
        layer_config = {"mask_layers": {}, "unmask": {}}

        parameters=self.Nodes.keys()
        has_down_layers=[]
        all_convs=[]
        for para in parameters:
            if self.Nodes[para].shape is not None and len(self.Nodes[para].shape)>=3:
                conv_layer=self.Nodes[para].para_name
                all_convs.append(conv_layer)
        for conv in   all_convs :

            if conv not in has_down_layers:
                has_down_layers.append(conv)
                main, slave, forward,flag = self.OpPath2Conv(conv)
                if main ==None or forward==None or len(forward)==0:
                    continue
                forward=list(set(forward).intersection(set(all_convs)))
                has_down_layers+=main
                has_down_layers+=slave



                if flag=='normal':
                    layer_config["mask_layers"][conv] = {'current_layer':
                                                            {'main': main, 'slave': slave}, 'forward_layer': forward, 'ops': 'normal',
                                                        'recommend_len': None}

                elif flag=='add' :
                    layer_config["mask_layers"][conv] = {'current_layer':
                                                            {'main': main, 'slave': slave}, 'forward_layer': forward, 'ops': 'add',
                                                        'recommend_len': None}



        print("self.save_yaml_pth", self.yaml_pth)
        with open(self.yaml_pth, "w") as f:
            yaml.safe_dump(layer_config, f, encoding='utf-8', allow_unicode=True)



if __name__ == "__main__":
    # sys.path.insert(0, '/opt/share1/hanjianhui/TestingCode/detect/Vihicle/yolov5-gyj')
    # model = torch.load('/opt/share1/hanjianhui/TestingCode/detect/Vihicle/yolov5-gyj/yolov5.pth', map_location='cpu')
    # data = torch.tensor(np.random.random(size=[1, 3, 960, 960])).to(torch.float32)
    # save_yaml_pth='./yolov5_use.yaml'
    #
    # AutoGenCovConnectLayer(model,data,save_yaml_pth,show=True)


    # jitmodel = torch.jit.trace(model, data)
    #
    # jitmodel.save('./JITmodel.libtorch')

    sys.path.insert(0, '/opt/share1/hanjianhui/TestingCode/detect/ssd.pytorch')
    from ssd import build_ssd

    ssd_net = build_ssd('test', 300, 2)
    data = torch.tensor(np.random.random(size=[1, 3, 300, 300])).to(torch.float32)
    DotMaker(ssd_net, data, './ssd.yaml')
