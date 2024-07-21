import torch
import yaml
import os
from collections import OrderedDict
import shutil

from thop import profile


class Pruner():
    def __init__(self,original_net,configs):
        self.original_net=original_net
        self.configs=configs
        self.save_pth=self.configs['save_pth']
        if os.path.exists(self.save_pth):

            shutil.rmtree(self.save_pth)
            os.makedirs(self.save_pth)

        else:
            os.makedirs(self.save_pth)

        try:
            inputs_shape = self.configs['dummy_input_shape']
            inputs = []
            for one in inputs_shape:
                input = torch.randn(one)
                inputs.append(input)

            self.inputs = tuple(inputs)
            self.validate()
            self.originale_flops, self.originale_paras = self.compute_flops()
        except:
            pass

    def __call__(self, *args, **kwargs):
        # assert  isinstance(self.inputs,tuple),"dummy_input_shape has down, don't use :pruner()"

        self.inputs = args

        self.validate()
        self.originale_flops, self.originale_paras = self.compute_flops()



    def forward(self):
        pass

    def compress(self):
        raise NotImplementedError

    # def test(self):
    #     raise NotImplementedError
    #
    # def train(self):
    #     raise NotImplementedError
    def compute_flops_call(self,*args):

        flops, params = profile(self.original_net, inputs=self.inputs, verbose=False)

        return flops,params
    def compute_flops(self):

        flops, params = profile(self.original_net, inputs=self.inputs, verbose=False)

        return flops,params

    def pruned_ratio(self):
        self.pruned_flops,self.pruned_paras=self.compute_flops()

        return self.pruned_flops/self.originale_flops,self.pruned_paras/self.originale_paras



    def validate(self):
        out=self.original_net(*self.inputs)
        print("****validate--------------> is OK")
        return out
    def save(self):
        try:
            torch.save(self.original_net,self.save_pth+'/pruned_model.pth')
            torch.save(self.original_net.state_dict(),self.save_pth+'/pruned_dict.pth')
        except:
            torch.save(self.original_net.state_dict(),self.save_pth+'/pruned_dict.pth')


class PruneGraph(Pruner):
    """
    mask model ----->    masked down model

    """

    def __init__(self, original_net, configs):
        super(PruneGraph,self).__init__(original_net,configs)



    def StepPrune(self,computed_layer_config,connected_layers):
        for key, info in connected_layers.items():
            print("**"*10,"The current layer is {}".format(key))
            if key not in computed_layer_config.keys():
                continue
            current_layer_main = info['current_layer']['main']
            current_layer_slave = info['current_layer']['slave']
            forward_layer = info['forward_layer']
            ops_type = info['ops']
            recommend_len=info['recommend_len']
            main_idx = None
            slave_idx = None
            forward_idx = None


            if ops_type == 'normal':
                """
                res2c_branch2b:
                    current_layer:
                      main: [res2c_branch2b, bn2c_branch2b, scale2c_branch2b]
                      slave: []
                    forward_layer: [res2c_branch2c]
                    ops: normal
                    recommend_len: null
                """
                for e_lay in current_layer_main:
                    if recommend_len is not None and len(recommend_len)>=1 and isinstance(recommend_len, list):
                        nozero_idx = recommend_len
                    elif e_lay in computed_layer_config :
                        nozero_idx=computed_layer_config[e_lay]

                    # if nozero_idx==None:
                    #     pass

                main_idx = nozero_idx
                slave_idx = nozero_idx
                forward_idx = nozero_idx

            elif ops_type == 'add':
                """
                res3a_branch1:
                    current_layer:
                      main: [bn3a_branch1, res3a_branch1, scale3a_branch1]
                      slave: [scale3a_branch2c, res3a_branch2c, bn3a_branch2c, res3d_branch2c, bn3b_branch2c,
                        scale3d_branch2c, res3c_branch2c, bn3d_branch2c, scale3b_branch2c, res3b_branch2c,
                        bn3c_branch2c, scale3c_branch2c]
                    forward_layer: [res3b_branch2a, res4a_branch1, res4a_branch2a, res3c_branch2a,
                      res3d_branch2a]
                    ops: add
                    recommend_len: null
                
                """
                for e_add in current_layer_main:
                    if recommend_len is not None and len(recommend_len)>=1 and isinstance(recommend_len, list):
                        nozero_idx = recommend_len

                    elif e_add in computed_layer_config:
                        nozero_idx=computed_layer_config[e_add]
                        break



                main_idx = nozero_idx
                slave_idx = nozero_idx
                forward_idx = nozero_idx

            elif ops_type == 'concat':
                """
                model.2.cv3.weight:
                    current_layer:
                      main:
                      - model.2.cv3.weight
                
                      slave: [[model.2.cv2.weight],]
                      slave2forward: [[model.2.bn.weight,model.2.bn.bias],]
                    forward_layer:
                
                     - model.2.cv4.conv.weight
                    ops: concat
                
                    recommend_len: null
              
                """
                slave2forward = info['current_layer']['slave2forward']

                nozero_len = 0
                for e_concat in current_layer_main:
                    if e_concat in computed_layer_config:
                        if recommend_len is not None and isinstance(recommend_len,list):
                            nozero_idx = recommend_len
                            nozero_len += len(nozero_idx)


                        else:
                            nozero_idx1 = computed_layer_config[e_concat]
                            nozero_idx = nozero_idx1
                            nozero_len += len(nozero_idx)

                        break
                self.PruneOp(main_layers=current_layer_main, slave_layers=None,
                             main_idx=nozero_idx, slave_idx=None, forward_idx=None,
                             forward_layers=None, current_fc=None, forward_fc=None)

                for e_concat in current_layer_slave:
                    slave_cat_idx = 0
                    for e_concat_sla in e_concat:

                        if e_concat_sla in computed_layer_config:

                            if recommend_len is not None and isinstance(recommend_len, list):
                                nozero_idx = recommend_len
                                nozero_len += len(nozero_idx)

                                slave_cat_idx=nozero_idx


                            else:
                                nozero_idx1 = computed_layer_config[e_concat_sla]
                                nozero_idx = nozero_idx1
                                nozero_len += len(nozero_idx)
                                slave_cat_idx = nozero_idx

                            break

                    self.PruneOp(main_layers=None, slave_layers=e_concat,
                                 main_idx=None, slave_idx=slave_cat_idx, forward_idx=None,
                                 forward_layers=None, current_fc=None, forward_fc=None)

                for e_concat_fw in forward_layer:
                    if e_concat_fw in computed_layer_config:
                        # if recommend_len is not None and isinstance(recommend_len, list):
                        #     nozero_idx = recommend_len
                        #
                        #
                        #
                        #
                        # else:
                        value =self.original_net.state_dict()[e_concat_fw]
                        value = torch.sum(torch.transpose(value,1,0),[1,2,3]).abs()

                        if value.shape[0] == nozero_len:
                            nozero_idx = [i for i in range(nozero_len)]

                        else:
                            layer_thr = torch.sort(value)[0][value.shape[0] - nozero_len - 1]

                            nozero_idx = torch.nonzero(value > layer_thr).squeeze().cpu().numpy().tolist()

                    self.PruneOp(main_layers=None, slave_layers=None,
                                 main_idx=None, slave_idx=None, forward_idx=nozero_idx,
                                 forward_layers=forward_layer, current_fc=None, forward_fc=None)

                    if len(slave2forward) >= 1:
                        for f2w in slave2forward:
                            if len(f2w) >= 1:
                                self.PruneOp(main_layers=None, slave_layers=f2w,
                                             main_idx=None, slave_idx=nozero_idx, forward_idx=None,
                                             forward_layers=None, current_fc=None, forward_fc=None)

                    break

                continue


            self.PruneOp(main_layers=current_layer_main, slave_layers=current_layer_slave,
                         main_idx=main_idx, slave_idx=slave_idx, forward_idx=forward_idx,
                         forward_layers=forward_layer,current_fc=None, forward_fc=None)





    def PruneOp_Conv(self, con_layer, channels="InChannel", Idx=None):
        layer_name = con_layer.strip().split('.')[0:-1]  # pop weight

        target_current_attr = None

        def current_att(attribute, idx):
            return attribute._modules[idx]



        if hasattr(self.original_net, '_modules'):
            target_current_attr = self.original_net
            for attr in layer_name:
                if attr == "module":
                    continue
                if hasattr(target_current_attr, '_modules'):
                    current_att_ = current_att(target_current_attr, attr)
                    target_current_attr = current_att_

        device = target_current_attr.weight.data.device

        if channels == "InChannel":
            try:
                target_current_attr.weight.data = torch.tensor(target_current_attr.weight.data[:, Idx, ...],
                                                               dtype=torch.float32).to(device)
                target_current_attr.in_channels = len(Idx)
            except:
                target_current_attr.weight.data = torch.tensor(target_current_attr.weight.data[:, Idx, ...],
                                                               dtype=torch.float32).to(device)
                target_current_attr.in_channels = len(Idx)

        elif channels == "OutChannel":

            target_current_attr.weight.data = torch.tensor(target_current_attr.weight.data[Idx], dtype=torch.float32).to(device)

            target_current_attr.out_channels = len(Idx)

    def PruneOp_bns(self, con_layer, channels="InChannel", Idx=None):

        layer_name = con_layer.strip().split('.')[0:-1]  # pop weight

        target_current_attr = None

        def current_att(attribute, idx):
            return attribute._modules[idx]



        if hasattr(self.original_net, '_modules'):
            target_current_attr = self.original_net
            for attr in layer_name:
                if attr == "module":
                    continue
                if hasattr(target_current_attr, '_modules'):
                    current_att_ = current_att(target_current_attr, attr)
                    target_current_attr = current_att_
        device = target_current_attr.weight.data.device

        if channels == "InChannel":
            pass
        elif channels == "OutChannel":
            if hasattr(target_current_attr, 'weight') and 'weight' in con_layer:
                target_current_attr.weight.data = torch.tensor(target_current_attr.weight.data[Idx],
                                                               dtype=torch.float32).to(device)

            if hasattr(target_current_attr, 'bias') and 'bias' in con_layer:
                # current_attr.weight.data = torch.ones(size=(channels,))
                target_current_attr.bias.data = torch.tensor(target_current_attr.bias.data[Idx], dtype=torch.float32).to(device)
            if hasattr(target_current_attr, 'num_features'):
                target_current_attr.num_features = len(Idx)
            if hasattr(target_current_attr, 'running_mean'):
                if target_current_attr.running_mean.data.shape[0]==target_current_attr.num_features:
                    pass
                else:
                    target_current_attr.running_mean.data = torch.tensor(target_current_attr.running_mean.data[Idx],
                                                                     dtype=torch.float32).to(device)
            if hasattr(target_current_attr, 'running_var'):
                if target_current_attr.running_var.data.shape[0]==target_current_attr.num_features:
                    pass
                else:
                    target_current_attr.running_var.data = torch.tensor(target_current_attr.running_var.data[Idx],
                                                                    dtype=torch.float32).to(device)



    def PruneOp(self, main_layers, slave_layers, main_idx, slave_idx, forward_idx, forward_layers,
                current_fc=None, forward_fc=None):
        Items_prune = self.original_net.state_dict()
        if main_layers is not None:

            for layer in main_layers:
                if len(Items_prune[layer].shape) == 4:
                    self.PruneOp_Conv(layer, channels="OutChannel", Idx=main_idx)

                else:
                    self.PruneOp_bns(layer, channels="OutChannel", Idx=main_idx)
                print("-m-|"*10,"Main layer are {}, these are OK!".format(layer))
        if slave_layers is not None:

            for slave in slave_layers:

                if len(Items_prune[slave].shape) == 4:
                    self.PruneOp_Conv(slave, channels="OutChannel", Idx=slave_idx)

                else:
                    self.PruneOp_bns(slave, channels="OutChannel", Idx=slave_idx)
                print("-s-" * 10, "Main layer are {}, these are OK!".format(slave))
        if forward_layers is not None:

            for forward in forward_layers:
                if len(Items_prune[forward].shape) == 4:
                    self.PruneOp_Conv(forward, channels="InChannel", Idx=forward_idx)
                print("->->" * 10, "Main layer are {}, these are OK!".format(forward))






