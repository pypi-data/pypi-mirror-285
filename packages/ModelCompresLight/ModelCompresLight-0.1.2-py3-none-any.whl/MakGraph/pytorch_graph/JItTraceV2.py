import yaml
import time

class IndexNode:
    def __init__(self,out,inputs,op,scope,shape,value,name):
        self.inputs=inputs
        self.out=out
        self.op=op
        self.scope=scope
        self.shape=shape
        self.value=value
        self.name=name
        self.cpp=None

class TreeNode:
    def __init__(self):
        self.nodes = dict()  # 构建字典
        self.is_leaf = False

    def insert(self, word: str):
        curr = self
        for char in word:
            if char not in curr.nodes:
                curr.nodes[char] = TreeNode()
            curr = curr.nodes[char]
        curr.is_leaf = True

    def insert_many(self, words: [str]):
        for word in words:
            self.insert(word)

    def search(self, word: str):
        curr = self
        for char in word:
            if char not in curr.nodes:
                return False
            curr = curr.nodes[char]
        return curr.is_leaf


class MakeJitGraph():
    """
    Generates model graph, each node is created from single or multiple jit trace nodes.
    """

    def __init__(self, model=None, dummy_input=None, yaml_pth=None):
        assert torch.__version__ >= '1.5.0'
        # model=model.eval().to(torch.device('cpu'))
        self.WeightsName=model.state_dict()
        self.yaml_pth=yaml_pth

        self._trace(model, dummy_input)

        self._build_graph()
        rr=self.FindPathToConv('model.2.cv2')
        # self.save_yaml()

    def _trace(self, model, dummy_input):

        self.trace = torch.jit.trace(model, dummy_input)
        torch._C._jit_pass_inline(self.trace.graph)




    def _extract_shape_info(self, node):
        """
        Extract the shape information of ```aten::view``` node

        Parameters
        ----------
        node : trace graph node
            It should be ```aten::view``` node

        Returns
        -------
        dict
            Include shape of input tensor and shape of output tensor
        """
        t_input = None
        for _input in node.inputs():
            t_input = _input
            break
        t_output = node.output()
        assert isinstance(t_input.type(), torch._C.TensorType)
        assert isinstance(t_output.type(), torch._C.TensorType)
        in_shape = t_input.type().sizes()
        out_shape = t_output.type().sizes()
        return {'in_shape': in_shape, 'out_shape': out_shape}

    def _extract_leaf_modules(self):
        """
        Extract leaf modules from the given graph. Leaf module means it does not have submodules.
        To extract leaf modules because only leaf module can be replaced. And shape inference can
        be done in leaf module level. Other shape inference is done in lower level i.e.,
        operation level.

        Returns
        -------
        list
            a list of scope name of all the leaf modules
        """

        def is_parent(name1, name2):
            """
            check if name1 is parent node of name2, for example:
            name1: aa.bb,  name2: aa.bb.cc,  return True
            name1: aa.b,  name2: aa.bb, return False
            """
            parts1, parts2 = name1.split('.'), name2.split('.')
            if len(parts1) >= len(parts2):
                return False
            for i, _ in enumerate(parts1):
                if parts2[i] != parts1[i]:
                    return False
            return True

        module_names = sorted([x[0]
                               for x in self.trace.named_modules() if x[0]])
        leaf_nodes = []
        for i, name in enumerate(module_names):
            if i + 1 >= len(module_names) or not is_parent(name, module_names[i + 1]):
                leaf_nodes.append(name)
        return leaf_nodes

    def _get_module_name(self, scope_name):
        """
        Retrieve module name from scope name.
        Parameters:
        -----------
        scope_name: str
            scope_name of a graph node, for example:
            for pytorch 1.3.1: MyModel/BackboneModel[backbone]/Conv2d[conv2]
            for pytorch 1.4.0: __module.backbone/__module.backbone.conv2

        Returns:
        -------
        str
            module name, such as backbone.conv2
        """
        if torch.__version__ >= '1.4.0':
            return scope_name.split('/')[-1].replace('__module.', '')
        else:
            return '.'.join(re.findall(r'\[(.*?)\]', scope_name))


    def _build_graph(self):

        graph = self.trace.graph
        IndexNodes= {x.debugName(): n for n in graph.nodes()
                          for x in n.outputs()}

        self.leaf_modules = self._extract_leaf_modules()


        for node in graph.nodes():
            outs=[x.debugName() for x in node.outputs()]
            inputs=[x.debugName()  for x in node.inputs()]
            op=node.kind()
            scope=self._get_module_name(node.scopeName())
            shape=None

            if op=="aten::_convolution":
                shape=self._extract_shape_info(node)
                outshape=shape['out_shape']
                shape=outshape
                #node.pyname node.attributeNames
                # module_names = sorted([x[0] for x in self.trace.named_modules() if x[0]])
                tensor_size = node.output()
                print(tensor_size)
            for ot in outs:
                IndexNodes[ot]=IndexNode(out=outs,inputs=inputs,op=op,scope=scope
            #
                                      ,shape=shape,value=None,name=None)

        self.IndexNodes=IndexNodes

    def FindOp(self,weigh_name):
        for key ,value in self.IndexNodes.items():
            if value.scope==weigh_name and value.op=="aten::_convolution":
                return key
    def FindBottom_is(self,index):
        path2conv=set()
        for key, value in self.IndexNodes.items():
            inuputs=value.inputs
            try:
                if inuputs is not None and index in inuputs:

                    path2conv.add(key)
            except:
                print(index)

        return list(path2conv)

    def IndexBottom(self,index):
        """
        current layer's bottom
        :param index:
        :return:
        """
        return self.IndexNodes[index].inputs

    def MakeTree(self):
        self.IndexNodes



    def FindPathToConv(self,weigh_name):
        op=self.FindOp(weigh_name)
        main_index=set()
        slave_index=set()
        forward_index=set()
        has_dealed_index=set()
        slave2forward=set()
        PathsDict={}
        PathOPs=set()
        def template(op):
            print("****op*******",op)
            PathOPs.add(self.IndexNodes[op].op)
            if self.IndexNodes[op].op not in ["aten::_convolution"]:

                FindBottom_is = self.FindBottom_is(op)
                indexsbottom = self.IndexBottom(op)
                has_dealed_index.add(op)
                PathsDict[op]=({"FindBottom_is":{e:self.IndexNodes[e] for e in FindBottom_is},"indexsbottom":{e:self.IndexNodes[e] for e in indexsbottom}},self.IndexNodes[op])

                for d in FindBottom_is:
                    print("---------FindBottom_is----------")
                    if d in list(has_dealed_index):
                        continue
                    info= self.IndexNodes[d]
                    if info.op=="prim::ListConstruct":
                        inputs=info.inputs
                        for input in  inputs:
                            if input in list(has_dealed_index):
                                continue

                            template(input)

                    elif    info.op in ["prim::GetAttr","prim::Constant"]:
                        pass

                    elif info.op in ["aten::batch_norm"]:
                        if self.IndexNodes[op].op in ["aten::cat"]:#
                            slave2forward.add(d)

                        slave_index.add(d)
                        inputs = info.inputs

                        for input in inputs:
                            if input in list(has_dealed_index):
                                continue

                            template(input)
                        template(d)

                    elif info.op in ["aten::_convolution"]:

                        # else:
                        forward_index.add(d)


                    else:

                        template(d)


                for u in indexsbottom:
                    print("---------indexsbottom----------")

                    if u in list(has_dealed_index):
                        continue
                    up_info= self.IndexNodes[u]
                    if up_info.op=="prim::ListConstruct":
                        inputs=up_info.inputs
                        for input in  inputs:
                            template(input)

                    elif   up_info.op in ["prim::GetAttr","prim::Constant"]:
                        pass

                    elif up_info.op in ["aten::batch_norm"]:
                        slave_index.add(u)

                        inputs = up_info.inputs
                        for input in inputs:
                            if self.IndexNodes[input].op in ["aten::_convolution"]:

                                slave_index.add(input)
                                continue
                            template(input)
                        template(u)

                    elif up_info.op in ["aten::_convolution"]:
                        slave_index.add(u)


                    else:

                        template(u)

        # first op

        first_bottom_is = self.FindBottom_is(op)
        main_index.add(op)
        for one in first_bottom_is:
            main_index.add(one)
            template(one)
        norm_add_cat='normal'
        if "aten::add" in list(PathOPs):
            norm_add_cat='add'
        elif "aten::cat" in list(PathOPs):
            norm_add_cat='concat'


        if len(list(main_index))==0 or  len(list(forward_index))==0:
            return None,None,None,None,None
        else:
            print( 'main layers',{e:self.IndexNodes[e].scope for e in list(main_index)})
            print( 'slave layers',{e:self.IndexNodes[e].scope for e in list(slave_index.difference(main_index).difference(slave2forward))})
            print( 'slave2forward layers',{e:self.IndexNodes[e].scope for e in list(slave2forward)})

            print( 'forward layers',{e:self.IndexNodes[e].scope for e in list(forward_index)})

            return self.CheckSuffix({e:self.IndexNodes[e].scope for e in list(main_index)}), \
                   self.CheckSuffix({e:self.IndexNodes[e].scope for e in list(slave_index.difference(main_index).difference(slave2forward))}), \
                   self.CheckSuffix({e:self.IndexNodes[e].scope for e in list(forward_index)}), \
                   self.CheckSuffix({e: self.IndexNodes[e].scope for e in list(slave2forward)}), \
                   norm_add_cat


    def CheckSuffix(self,layer):
        new_layer=[]
        for k,value in layer.items():
            if value+".weight" in self.WeightsName.keys():
                new_layer.append(value+".weight")
            if value+".bias" in self.WeightsName.keys():
                new_layer.append(value+".bias")
            if value + ".running_mean" in self.WeightsName.keys():
                new_layer.append(value + ".running_mean")
            if value + ".running_var" in self.WeightsName.keys():
                new_layer.append(value + ".running_var")

        return new_layer

    def save_yaml(self):
        layer_config = {"mask_layers": {}, "unmask": {}}

        parameters = self.WeightsName.keys()
        has_down_layers = []
        all_convs = []

        for para in parameters:
            if self.WeightsName[para].shape is not None and len(self.WeightsName[para].shape) >= 3:
                all_convs.append(para)

        for conv in all_convs:

            if conv not in has_down_layers:
                has_down_layers.append(conv)

                main, slave, forward ,s2f,flag= self.FindPathToConv('.'.join(conv.split('.')[:-1]))
                if slave is not None:
                    has_down_layers+=slave
                if s2f is not None:
                    has_down_layers+=s2f

                if main is None:
                    print("--------This layer config is -----------",conv)
                    continue

                if flag=='normal':
                    layer_config["mask_layers"][conv] = {'current_layer':
                                                             {'main': main, 'slave': slave}, 'forward_layer': forward,
                                                         'ops': 'normal',
                                                         'recommend_len': None}

                elif flag=='add':
                    layer_config["mask_layers"][conv] = {'current_layer':
                                                             {'main': main, 'slave': slave}, 'forward_layer': forward,
                                                         'ops': 'add',

                                                         'recommend_len': None}
                elif flag=='concat':

                    def is_parent(name1, name2):
                        """
                        check if name1 is parent node of name2, for example:
                        name1: aa.bb,  name2: aa.bb.cc,  return True
                        name1: aa.b,  name2: aa.bb, return False
                        """
                        parts1, parts2 = name1.split('.'), name2.split('.')
                        if len(parts1) >= len(parts2):
                            return False
                        for i, _ in enumerate(parts1):
                            if parts2[i] != parts1[i]:
                                return False
                        return True
                    new_s2f=[]
                    prefix=set()
                    for one in s2f:
                        prefix_='.'.join(one.split('.')[:-1])
                        prefix.add(prefix_)

                    for pre in list(prefix):
                        tmp=[]
                        for e in s2f:
                            if is_parent(pre,e):
                                tmp.append(e)
                        new_s2f.append(tmp)


                    layer_config["mask_layers"][conv] = {'current_layer':
                                                             {'main': main, 'slave': [slave],
                                                              'slave2forward':new_s2f

                                                              }, 'forward_layer': forward,
                                                         'ops': 'concat',

                                                         'recommend_len': None}




        print("self.save_yaml_pth", self.yaml_pth)
        with open(self.yaml_pth, "w") as f:
            yaml.safe_dump(layer_config, f, encoding='utf-8', allow_unicode=True)





if __name__ == "__main__":
    import os
    import numpy as np
    import torch
    import sys
    import re

    sys.path.insert(0, '/opt/share1/hanjianhui/TestingCode/detect/Vihicle/yolov5-gyj')
    model = \
        torch.load('/opt/share1/hanjianhui/TestingCode/detect/Vihicle/yolov5-gyj/log_bdd/run_car/exp0/weights/last.pt',
                   map_location='cpu')['model']
    data = torch.tensor(np.random.random(size=[1, 3, 960, 960])).to(torch.float32)

    AutoGraph_ = MakeJitGraph(model, data,yaml_pth='./yolov5_use.yaml')  # TorchModuleGraph
    trace_graph = AutoGraph_.trace.graph





