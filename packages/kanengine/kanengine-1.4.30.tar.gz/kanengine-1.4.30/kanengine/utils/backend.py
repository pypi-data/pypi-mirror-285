import json
from pathlib import Path
from collections import OrderedDict, namedtuple

import torch
import numpy as np

from .export import expoort_in_subprocess

__all__ = ['TorchScriptBackend', 'ONNXRuntimeBackend', 'TensorRTBackend', 'AutoBackend']


def convert_fp16(data):
    """转换模型为FP16"""

    if isinstance(data, torch.Tensor) and data.dtype != torch.float16:
        data = data.to(torch.float16)

    elif isinstance(data, np.ndarray) and data.dtype != np.float16:
        data = data.astype(np.float16)

    return data


def transform_type(data, to_torch=False, to_numpy=False, to_fp16=False, device=False, new_torch=False):
    """
    将数据转换为torch.Tensor或numpy.ndarray类型

    Args:
        data (torch.Tensor or np.ndarray): 待转换的数据
        to_torch (bool): 是否转换为torch.Tensor类型
        to_numpy (bool): 是否转换为numpy.ndarray类型
        to_fp16 (bool): 是否转换为FP16类型
        device (bool, torch.device): 是否将数据转移到指定设备
        new_torch (bool): 当数据为numpy.ndarray类型且to_torch为True时，该参数表示是否创建新的torch.Tensor类型

    Returns:
        (torch.Tensor or np.ndarray): 转换后的数据
    """

    # 若数据为numpy.ndarray类型且to_torch为True，则转换为torch.Tensor类型
    if isinstance(data, np.ndarray) and to_torch:
        if new_torch:
            data = torch.tensor(data)
        else:
            data = torch.from_numpy(data)

    # 若数据为torch.Tensor类型且to_numpy为True，则转换为numpy.ndarray类型
    if isinstance(data, torch.Tensor) and to_numpy:
        data = data.cpu().numpy()

    if to_fp16:
        data = convert_fp16(data)

    if device and isinstance(data, torch.Tensor) and data.device != device:
        data = data.to(device)

    return data


class BaseBackend(object):
    def __init__(self, weight_path: str, device: str | torch.device = 'cuda:0', fp16=False, **kwargs):
        self.weight_path = weight_path
        self.device = torch.device(device) if isinstance(device, str) else device
        self.fp16 = fp16
        self.kwargs = kwargs
        self.load_weight()

    def __call__(self, im):
        """
        将图像输入模型进行推理，并返回推理结果
        Args:
            im (np.ndarray or torch.Tensor): 输入图像
        Returns:
            (torch.Tensor or numpy.ndarray): 模型推理结果
        """

    def load_weight(self):
        """加载模型"""


class TorchScriptBackend(BaseBackend):

    def load_weight(self):
        self.model = torch.jit.load(self.weight_path, map_location=self.device)
        self.model.half() if self.fp16 else self.model.float()
        self.model.eval()

    def __call__(self, im):
        im = transform_type(im, to_torch=True, to_fp16=self.fp16, device=self.device)
        y = self.model(im)
        return y


class ONNXRuntimeBackend(BaseBackend):

    def load_weight(self):
        import onnxruntime
        cuda = self.device.type != "cpu"
        cuda_providers = [
            ('CUDAExecutionProvider', {
                'device_id': self.device.index,
                'arena_extend_strategy': 'kNextPowerOfTwo',
                'gpu_mem_limit': 10 * 1024 * 1024 * 1024,
                'cudnn_conv_algo_search': 'EXHAUSTIVE',
            }),
            'CPUExecutionProvider',
        ]
        providers = cuda_providers if cuda else ["CPUExecutionProvider"]
        self.session = onnxruntime.InferenceSession(self.weight_path, providers=providers)
        self.output_names = [x.name for x in self.session.get_outputs()]
        self.input_name = self.session.get_inputs()[0].name

    def __call__(self, im):
        im = transform_type(im, to_numpy=True, to_fp16=self.fp16)
        y = self.session.run(self.output_names, {self.input_name: im})

        return y


class TensorRTBackend(BaseBackend):

    def check_engine(self):
        if Path(self.weight_path).exists():
            return True

        # 检查onnx文件是否存在
        onnx_path = self.weight_path.replace(".engine", ".onnx")
        if Path(onnx_path).exists() is False:
            raise FileNotFoundError(f"ONNX 文件不存在: {onnx_path}")

        # 导出TensorRT引擎
        return_code = expoort_in_subprocess(
            f_onnx=onnx_path,
            dynamic=True,
            half=self.fp16,
            input_shape=self.kwargs['input_shape']
        )

        if return_code != 0:
            raise RuntimeError(f"导出TensorRT引擎失败: {self.weight_path}")

    def load_weight(self):
        import tensorrt as trt

        self.check_engine()
        Binding = namedtuple("Binding", ("name", "dtype", "shape", "data", "ptr"))
        logger = trt.Logger(trt.Logger.INFO)
        with open(self.weight_path, "rb") as f, trt.Runtime(logger) as runtime:
            # meta_len = int.from_bytes(f.read(4), byteorder="little")  # read metadata length
            # metadata = json.loads(f.read(meta_len).decode("utf-8"))  # read metadata
            model = runtime.deserialize_cuda_engine(f.read())
        context = model.create_execution_context()
        bindings = OrderedDict()
        output_names = []
        dynamic = False
        shape_dict = {}
        for i in range(model.num_bindings):
            name = model.get_binding_name(i)
            dtype = trt.nptype(model.get_binding_dtype(i))
            if model.binding_is_input(i):
                if -1 in tuple(model.get_binding_shape(i)):
                    dynamic = True
                    context.set_binding_shape(i, tuple(model.get_profile_shape(0, i)[2]))
                if dtype == np.float16:
                    self.fp16 = True
            else:
                output_names.append(name)
            shape = tuple(context.get_binding_shape(i))
            shape_dict[name] = shape
            im = torch.from_numpy(np.empty(shape, dtype=dtype)).to(self.device)
            bindings[name] = Binding(name, dtype, shape, im, int(im.data_ptr()))
        binding_addrs = OrderedDict((n, d.ptr) for n, d in bindings.items())
        batch_size = bindings["images"].shape[0]
        self.dynamic = dynamic
        self.bindings = bindings
        self.output_names = output_names
        self.context = context
        self.binding_addrs = binding_addrs
        self.batch_size = batch_size
        self.model = model

    def __call__(self, im):
        im = transform_type(im, to_torch=True, to_fp16=self.fp16, device=self.device)

        if self.dynamic and im.shape != self.bindings["images"].shape:
            i = self.model.get_binding_index("images")
            self.context.set_binding_shape(i, im.shape)
            self.bindings["images"] = self.bindings["images"]._replace(shape=im.shape)
            for name in self.output_names:
                i = self.model.get_binding_index(name)
                self.bindings[name] = self.bindings[name]._replace(shape=tuple(self.context.get_binding_shape(i)))
        s = self.bindings["images"].shape
        assert im.shape == s, f"input size {im.shape} {'>' if self.dynamic else 'not equal to'} max model size {s}"
        self.binding_addrs["images"] = int(im.data_ptr())
        self.context.execute_v2(list(self.binding_addrs.values()))
        y = [self.bindings[x][3] for x in sorted(self.output_names)]

        return y


class AutoBackend(object):
    """
    自动选择合适的推理引擎
    """

    def __init__(self, weight_path: str, device: str = 'cuda:0', fp16=False, **kwargs):
        self.device = torch.device(device) if isinstance(device, str) else device
        suffix = Path(weight_path).suffix
        match suffix:
            case ".pth" | ".torchscript":
                self.backend = TorchScriptBackend(weight_path, device, fp16, **kwargs)
            case ".onnx":
                self.backend = ONNXRuntimeBackend(weight_path, device, fp16, **kwargs)
            case ".engine":
                self.backend = TensorRTBackend(weight_path, device, fp16, **kwargs)
            case _:
                raise ValueError(f"Unsupported weight file suffix: {suffix}")

    def __call__(self, im, to_torch=True, to_device=True):
        """
        将图像输入模型进行推理，并返回推理结果

        Args:
            im (np.ndarray or torch.Tensor): 输入图像
            to_torch (bool): 是否将推理结果转换为torch.Tensor类型
            to_device (bool): 是否将推理结果数据转移到指定设备

        Returns:
            (torch.Tensor or numpy.ndarray): 模型推理结果
        """

        y = self.backend(im)
        device = self.device if to_device else False

        if isinstance(y, (list, tuple)) and len(y) > 1:
            return [transform_type(x, to_torch=to_torch, device=device) for x in y]

        if isinstance(y, (list, tuple)) and len(y) == 1:
            return transform_type(y[0], to_torch=to_torch, device=device, new_torch=True)

        if isinstance(self.backend, TorchScriptBackend):
            return y

        if isinstance(y, (np.ndarray, torch.Tensor)):
            return transform_type(y, to_torch=to_torch, device=device)
