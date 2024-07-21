from __future__ import absolute_import
import sys
import yaml
import torch
from Compression.PyTorch.prune.GraphPrune import PruneGraph
from Compression.PyTorch.prune.Weight.compute_bn import Batch_Norm
from Compression.PyTorch.prune.Weight.compute_conv import Compute_conv_fpgm


class FPGM_conv_prune(PruneGraph):
    def __init__(self, orinet, configs):
        super(FPGM_conv_prune,self).__init__(orinet, configs)
        # self.compress()

    def compress(self):
        """
        calculate ids ---> load yaml--->step prune --->validate --->save pruned model --->return model

        :return:
        """
        self.cacl_prune()
        yaml_config = yaml.load(open(self.configs['layer_config']))

        self.mask_layers = yaml_config['mask_layers']
        self.StepPrune(computed_layer_config=self.layers_pruned_config,connected_layers=self.mask_layers)
        self.get_pruned_paras()
        print("------Pruned Model is OK, the next is to compute acc/loss------")

        self.validate()
        if self.save_pth:
            self.save()
        return self.original_net
    def get_pruned_paras(self):

        pruned_para=[(k, v.shape) for k, v in dict(self.original_net.named_parameters()).items()]
        print("------PrunedModelParameters------",pruned_para)



    def cacl_prune(self):
        self.layers_pruned_config = Compute_conv_fpgm(self.original_net, pru_ratio=self.configs['prune_ration'], use_global_bn=self.configs['global']).layer_thrs


    def train(self):
        pass

    def test(self):
        pass

    def wrap_yaml(self):
        pass



# if __name__ == "__main__":
#     config={
#
#         'layer_config':'/opt/share1/hanjianhui/syccode/PytorchModelCompression/graph/pytorch_graph/yolov5_use.yaml',
#         'prune_ration': 0.1,
#         'global':True,
#         'save_pth':'../../tmp'
#
#     }
#     sys.path.insert(0, '/opt/share1/hanjianhui/TestingCode/detect/Vihicle/yolov5-gyj')
#     model = torch.load('/opt/share1/hanjianhui/TestingCode/detect/Vihicle/yolov5-gyj/yolov5.pth', map_location='cpu')
#
#     Dot_gen = Ln_bn_prune(model, config)
#     pruned_model=Dot_gen.compress()
#     print(Dot_gen)
