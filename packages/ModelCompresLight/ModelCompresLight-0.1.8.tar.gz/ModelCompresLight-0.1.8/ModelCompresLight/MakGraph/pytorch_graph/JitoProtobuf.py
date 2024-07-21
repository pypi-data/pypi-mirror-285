# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.


import logging
import queue
import re
from collections import defaultdict
import torch
from torch.utils.tensorboard._pytorch_graph import NodePy, NodePyIO, NodePyOP, GraphPy
CLASSTYPE_KIND = 'ClassType'
GETATTR_KIND = 'prim::GetAttr'
CAT_KIND = 'aten::cat'
LIST_CONSTRUCT_KIND = 'prim::ListConstruct'
LIST_UNPACK_KIND = 'prim::ListUnpack'
TUPLE_CONSTRUCT_KIND = 'prim::TupleConstruct'
TUPLE_UNPACK_KIND = 'prim::TupleUnpack'

_logger = logging.getLogger(__name__)



def parse_traced_name(module_name):
    prefix = 'TracedModule['
    suffix = ']'
    if module_name.startswith(prefix) and module_name.endswith(suffix):
        module_name = module_name[len(prefix):-len(suffix)]
    return module_name


class TorchGraph:
    """
    This class is to extract pytorch model topology graph by tracing
    """

    def __init__(self, model=None, dummy_input=None, traced_model=None):
        """
        Parameters
        ----------
        model : pytorch model
            The model user wants to speed up
        dummy_input : pytorch tensor
            The dummy input for ```jit.trace```, users should put it on right device before pass in
        traced_model : torch._C.torch.jit.TopLevelTracedModule
            An alredy traced model, if traced_model is not None, then TorchGraph will build the graph
            based on this traced model and won't trace the model again.
        """
        assert torch.__version__ >= '1.3.1'
        # check if the input is legal
        if traced_model is not None:
            assert isinstance(traced_model, torch.jit.TopLevelTracedModule)
            self.trace = traced_model
            # it's ok if the graph is already unpacked
            torch._C._jit_pass_inline(self.trace.graph)
        elif model is not None and dummy_input is not None:
            self.bound_model = model
            self._trace(model, dummy_input)
        else:
            raise Exception(
                'Please provide model & dummy_input or the traced_model as inputs')

    def _trace(self, model, dummy_input):
        with torch.onnx.set_training(model, False):
            self.trace = torch.jit.trace(model, dummy_input)
            torch._C._jit_pass_inline(self.trace.graph)


class TorchProtoGraph(TorchGraph):
    """
    Generates model graph for pytorch models in protobuf, this implementation
    is borrowed from pytorch v1.4.0, and fixed following issues:
    https://github.com/pytorch/pytorch/issues/33691
    https://github.com/pytorch/pytorch/issues/33670

    """

    def __init__(self, model, dummy_input, verbose=False):
        super().__init__(model, dummy_input)

        from tensorboard.compat.proto.config_pb2 import RunMetadata
        from tensorboard.compat.proto.graph_pb2 import GraphDef
        from tensorboard.compat.proto.step_stats_pb2 import StepStats, DeviceStepStats
        from tensorboard.compat.proto.versions_pb2 import VersionDef

        list_of_nodes = self.parse(self.trace.graph, self.trace, dummy_input)
        if verbose:
            print(self.trace.graph)
        self.stepstats = RunMetadata(step_stats=StepStats(
            dev_stats=[DeviceStepStats(device="/device:CPU:0")]))
        self.graph_def = GraphDef(
            node=list_of_nodes, versions=VersionDef(producer=22))

    def parse(self, graph, trace, args=None, omit_useless_nodes=True):
        """This method parses an optimized PyTorch model graph and produces
        a list of nodes and node stats for eventual conversion to TensorBoard
        protobuf format.

        Args:
        graph (PyTorch module): The model graph to be parsed.
        trace (PyTorch JIT TracedModule): The model trace to be parsed.
        args (tuple): input tensor[s] for the model.
        omit_useless_nodes (boolean): Whether to remove nodes from the graph.
        """
        nodes_py = GraphPy()
        for node in graph.inputs():
            if omit_useless_nodes:
                if not node.uses():  # number of user of the node (= number of outputs/ fanout)
                    continue

            if node.type().kind() != CLASSTYPE_KIND:
                nodes_py.append(NodePyIO(node, 'input'))

        attr_to_scope = dict()

        def node_to_name(d):
            return str(d).split(":")[0].strip()
        for node in graph.nodes():
            if node.kind() == GETATTR_KIND:
                attr_name = node.s('name')
                node_name = node_to_name(node)
                parent = node.input().node()
                # If the parent node is not the top-level "self" node
                if parent.kind() == GETATTR_KIND:
                    parent_scope = attr_to_scope[node_to_name(parent)]
                    attr_scope = parent_scope.split('/')[-1]
                    attr_to_scope[node_name] = '{}/{}.{}'.format(
                        parent_scope, attr_scope, attr_name)
                else:
                    attr_to_scope[node_name] = '__module.{}'.format(attr_name)
                # We don't need classtype nodes; scope will provide this information
                if node.output().type().kind() != CLASSTYPE_KIND:
                    node_py = NodePyOP(node)
                    node_py.scopeName = attr_to_scope[node_name]
                    nodes_py.append(node_py)
            else:
                nodes_py.append(NodePyOP(node))

        # Create sink nodes for output ops
        for i, node in enumerate(graph.outputs()):
            node_py = NodePyIO(node, 'output')
            node_py.debugName = "output.{}".format(i + 1)
            node_py.inputs = [node.debugName()]
            nodes_py.append(node_py)

        alias_to_name = dict()
        base_name = parse_traced_name(trace._name)
        for name, module in trace.named_modules(prefix='__module'):
            mod_name = parse_traced_name(module._name)
            attr_name = name.split('.')[-1]
            alias_to_name[name] = '{}[{}]'.format(mod_name, attr_name)

        for node in nodes_py.nodes_op:
            module_aliases = node.scopeName.split('/')[-1].split('.')
            module_name = ''
            for i, alias in enumerate(module_aliases):
                if i == 0:
                    module_name = alias
                    node.scopeName = base_name
                else:
                    module_name += '.' + alias
                    node.scopeName += '/' + \
                        (alias_to_name[module_name]
                         if module_name in alias_to_name else alias)

        nodes_py.populate_namespace_from_OP_to_IO()
        return nodes_py.to_proto()


class NodePyGroup(NodePy):
    """
    This class is used to represent a graph node which consists of multiple jit traced nodes. In a pytorch trace graph,
    there are multiple nodes are traced for one torch.nn.Module object, we group them together to form a single node to
    represent the torch.nn.Module object. We also group some functional call trace nodes together to form a new node.
    """

    def __init__(self, name, unique_name, node_type, op_type, node_cpps, inputs=None, outputs=None, key_node=None):
        """
        Parameters:
        -----------
        name: str
            node name, such as `conv1`, `backbone.classifier`
        unique_name: str
            A global unique name for current node. Due to some modules,
            such as relu, may be reused several times, so the scopename
            is not suitable as the global unique identifier, so we add a
            unique_name for each node as the global unique identifier.
            We should use the unique_name to traverset the module graph.
        node_type: str
            `module` or `func`
        op_type: str
            operation type, such as `Conv2d`, `aten::view`
        node_cpps: list of torch._C.Node
            jit trace nodes which are included in this new node
        inputs: list of str
            All the inputs of this node, each element is debugName of one input
        outputs: list of str
            All the outputs of this node, each element is debugName of one output
        key_node: torch._C.Node
            The key node of this NodePyGroup.
        """
        super(NodePyGroup, self).__init__(name, [])
        self.node_cpps = node_cpps
        self.name = name
        self.unique_name = unique_name
        self.op_type = op_type
        self.type = node_type
        self.nodes = []
        self.auxiliary = None
        self.add_nodes(node_cpps)
        self.inputs = inputs
        self.outputs = outputs
        # The core node in this NodePyGroup
        self.key_node = key_node

    def add_nodes(self, node_cpps):
        for node_cpp in node_cpps:
            nodepy = NodePyOP(node_cpp)
            nodepy.name = node_cpp.scopeName() + '_' + node_cpp.kind()
            self.nodes.append(nodepy)

    def sub_node_names(self):
        return [x.name for x in self.nodes]

    def __repr__(self):
        return 'name: {}, type: {}, op_type: {}, sub_nodes: {}, inputs: {}, outputs: {}, aux: {}'.format(
            self.name, self.type, self.op_type, self.sub_node_names(),
            self.inputs, self.outputs, self.auxiliary
        )




if __name__=="__main__":
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

    AutoGraph_ = TorchProtoGraph(model,data)

