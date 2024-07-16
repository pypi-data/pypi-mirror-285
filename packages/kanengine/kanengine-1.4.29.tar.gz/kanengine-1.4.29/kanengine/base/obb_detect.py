"""
    旋转框检测器
"""

from typing import TypeAlias

import torch
import numpy as np

from ..abc import EngineABC
from ..utils import ops, AutoBackend

ConfArg: TypeAlias = dict[int, float]
ConfArgs: TypeAlias = list[ConfArg]
OrigImg: TypeAlias = np.ndarray
OrigImgs: TypeAlias = list[OrigImg]


class BaseObbDetector(EngineABC):

    def __init__(self, weight_path: str, device: list[int], fp16: bool, input_size=(640, 640)):
        super().__init__()
        self.model = {}
        self.device = {}

        self._input_size = input_size
        # 加载模型到多个GPU
        for index, device_i in enumerate(device):
            t_device = f'cuda:{device_i}' if torch.cuda.is_available() and device_i >= 0 else 'cpu'
            model = AutoBackend(weight_path, t_device, fp16, input_shape=(1, 3, *input_size))
            self.model[index] = model
            self.device[index] = t_device

        self.fp16 = fp16
        self._i = 0
        self._device_num = len(self.device)
        self._warmup()

    def _get_device_model(self):
        """获取某个显卡上的model和device"""

        self._i += 1
        index = self._i % self._device_num
        model = self.model[index]
        device = self.device[index]

        return model, device

    def _warmup(self):
        """预热"""
        _, device = self._get_device_model()
        num_warmup = 5 if device == 'cpu' else 50
        for _ in range(num_warmup):
            model, device = self._get_device_model()
            dtype = torch.float16 if self.fp16 else torch.float32
            arr = torch.randn((1, 3, *self._input_size), device=device, dtype=dtype)
            model(arr)

    def __call__(self, orig_img: OrigImgs | OrigImg, conf_arg: ConfArgs | ConfArg | float = 0.25):

        model, device = self._get_device_model()
        is_one = not isinstance(orig_img, list)
        orig_img = [orig_img] if is_one else orig_img
        tensor_im = self._preprocess(orig_img, device)
        preds = self._infer(tensor_im, model)
        args = tensor_im, orig_img, conf_arg
        processed_pred = self._postprocess(preds, *args)
        processed_pred = processed_pred[0] if is_one and processed_pred else processed_pred
        return processed_pred

    def _infer(self, im: torch.Tensor, model) -> torch.Tensor:
        """推理"""
        return model(im)

    def _preprocess(self, ims: list[np.ndarray], device):
        # 原始图像尺寸 --> 模型推理的输入图像尺寸
        ims = [ops.adjust_scale(im, new_shape=self._input_size) for im in ims]
        ims = np.stack(ims, 0)
        ims = ims[..., ::-1].transpose(0, 3, 1, 2)  # BHWC --> BCHW
        ims = np.ascontiguousarray(ims)

        # np.ndarray 转换成 torch.tensor
        tensor_ims = torch.from_numpy(ims).to(device)
        tensor_ims = tensor_ims.half() if self.fp16 else tensor_ims.float()
        tensor_ims /= 255.0

        return tensor_ims

    def _postprocess(self, preds, *args):
        """
        后处理
        Parameters
        ----------
        preds: torch.Tensor
            模型输出的预测结果
        args: tuple
            预处理所需的参数，包括原始图像、nms参数等

        Returns
        -------
        processed_preds: list[np.ndarray]
            处理后的预测结果
        """

        # TODO:对不同的目标进行nms时使用的置信度阈值不同，需要修改
        tensor_ims, orig_imggs, nms_args = args
        nms_args = {0: nms_args} if isinstance(nms_args, float) else nms_args
        conf_thres = list(nms_args[0].values())[0] if isinstance(nms_args, list) else list(nms_args.values())[0]
        preds = ops.non_max_suppression(
            preds,
            conf_thres=conf_thres,
            iou_thres=0.45,
            rotated=True,
        )
        processed_preds = []

        for pred, tensor_im, orig_imgg in zip(preds, tensor_ims, orig_imggs):
            rboxes = ops.regularize_rboxes(torch.cat([pred[:, :4], pred[:, -1:]], dim=-1))
            rboxes[:, :4] = ops.scale_boxes(tensor_im.shape[-2:], rboxes[:, :4], orig_imgg.shape, xywh=True)
            # xywh, r, conf, cls
            obb = torch.cat([rboxes, pred[:, 4:6]], dim=-1)
            processed_preds.append(obb.to('cpu').numpy())

        return processed_preds
