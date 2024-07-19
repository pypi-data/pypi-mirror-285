from MakGraph.pytorch_graph.BackWardGraph import DotMaker
from MakGraph.pytorch_graph.JItTrace import MakeJitGraph

import sys
import torch
def AutoGenCovConnectLayer(model,data,save_pth,show=True):
    graph=DotMaker(model,data,save_pth)
    if show:
        graph.ShowGarph()


def AutoGenCovConnectLayerByJit(model,data,save_pth,show=True):
    AutoGraph_=MakeJitGraph(model,data,save_pth)
    if show:
        AutoGraph_.trace.save('./JitShowByNetron.pt')
        with open('JitShowByNetron.txt','w') as fi:
            fi.write(str(AutoGraph_.trace.graph))
