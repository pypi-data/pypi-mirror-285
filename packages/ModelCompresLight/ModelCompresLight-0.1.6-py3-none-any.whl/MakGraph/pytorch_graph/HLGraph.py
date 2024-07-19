import os
import numpy as np
import torch
import sys
import re
sys.path.insert(0,'/opt/share1/hanjianhui/TestingCode/detect/Vihicle/yolov5-gyj')
model=torch.load('/opt/share1/hanjianhui/TestingCode/detect/Vihicle/yolov5-gyj/log_bdd/run_car/exp0/weights/last.pt',map_location='cpu')['model']
data=torch.tensor(np.random.random(size=[1,3,960,960])).to(torch.float32)

# trace, out = torch.jit._get_trace_graph(model, data)
# with torch.onnx.set_training(model, False):
#     trace = torch.jit.trace(model, data)

# with torch.onnx.set_training(model, False):
#     trace =torch._C._jit_pass_inline(torch.jit.trace(model, data).inlined_graph)

trace =torch.jit.trace(model, data).inlined_graph

def get_shape(torch_node):
    """Return the output shape of the given Pytorch node."""
    # Extract node output shape from the node string representation
    # This is a hack because there doesn't seem to be an official way to do it.
    # See my quesiton in the PyTorch forum:
    # https://discuss.pytorch.org/t/node-output-shape-from-trace-graph/24351/2
    # TODO: find a better way to extract output shape
    # TODO: Assuming the node has one output. Update if we encounter a multi-output node.
    m = re.match(r".*Float\(([\d\s\,]+)\).*", str(next(torch_node.outputs())))
    if m:
        shape = m.group(1)
        shape = shape.split(",")
        shape = tuple(map(int, shape))
    else:
        shape = None
    return shape
class Node():
    """Represents a framework-agnostic neural network layer in a directed graph."""

    def __init__(self, uid, name, op, output_shape=None, params=None):
        """
        uid: unique ID for the layer that doesn't repeat in the computation graph.
        name: Name to display
        op: Framework-agnostic operation name.
        """
        self.id = uid
        self.name = name  # TODO: clarify the use of op vs name vs title
        self.op = op
        self.repeat = 1
        if output_shape:
            assert isinstance(output_shape, (tuple, list)),\
            "output_shape must be a tuple or list but received {}".format(type(output_shape))
        self.output_shape = output_shape
        self.params = params if params else {}
        self._caption = ""

    @property
    def title(self):
        # Default
        title = self.name or self.op

        if "kernel_shape" in self.params:
            # Kernel
            kernel = self.params["kernel_shape"]
            title += "x".join(map(str, kernel))
        if "stride" in self.params:
            stride = self.params["stride"]
            if np.unique(stride).size == 1:
                stride = stride[0]
            if stride != 1:
                title += "/s{}".format(str(stride))
        #         # Transposed
        #         if node.transposed:
        #             name = "Transposed" + name
        return title

    @property
    def caption(self):
        if self._caption:
            return self._caption

        caption = ""

        # Stride
        # if "stride" in self.params:
        #     stride = self.params["stride"]
        #     if np.unique(stride).size == 1:
        #         stride = stride[0]
        #     if stride != 1:
        #         caption += "/{}".format(str(stride))
        return caption

    def __repr__(self):
        args = (self.op, self.name, self.id, self.title, self.repeat)
        f = "<Node: op: {}, name: {}, id: {}, title: {}, repeat: {}"
        if self.output_shape:
            args += (str(self.output_shape),)
            f += ", shape: {:}"
        if self.params:
            args += (str(self.params),)
            f += ", params: {:}"
        f += ">"
        return f.format(*args)
def pytorch_id(node):
    """Returns a unique ID for a node."""
    # After ONNX simplification, the scopeName is not unique anymore
    # so append node outputs to guarantee uniqueness
    return node.scopeName() + "/outputs/" + "/".join(["{}".format(o.unique()) for o in node.outputs()])

all=dict()

for torch_node in trace.nodes():
    # Op
    op = torch_node.kind()
    # Parameters
    params = {k: torch_node[k] for k in torch_node.attributeNames()}
    # Inputs/outputs
    # TODO: inputs = [i.unique() for i in node.inputs()]
    outputs = [o.unique() for o in torch_node.outputs()]
    # Get output shape
    shape = get_shape(torch_node)
    # Add HL node
    all[pytorch_id(torch_node)] = Node(uid=pytorch_id(torch_node), name=None, op=op,
                   output_shape=shape, params=params)
    # Add edges
    # for target_torch_node in torch_node.nodes():
    #     target_inputs = [i.unique() for i in target_torch_node.inputs()]
    #     if set(outputs) & set(target_inputs):
    #         print(target_torch_node)
print(all)