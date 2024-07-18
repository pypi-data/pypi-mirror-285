"""
    基础检测器
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


class BaseDetector(EngineABC):

    def __init__(self, weight_path: str, device: list[int], fp16: bool, input_size=(640, 640)) -> None:
        self.model = {}
        self.device = {}

        # 加载模型到多个GPU
        for index, device_i in enumerate(device):
            t_device = f'cuda:{device_i}' if torch.cuda.is_available() and device_i >= 0 else 'cpu'
            model = AutoBackend(weight_path, t_device, fp16, input_shape=(1, 3, *input_size))
            self.model[index] = model
            self.device[index] = t_device

        self.fp16 = fp16
        self._input_size = input_size
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
        num_warmup = 5 if device == 'cpu' else 70

        for _ in range(num_warmup):
            model, device = self._get_device_model()
            arr = torch.randn((1, 3, *self._input_size), device=device)
            arr = arr.half() if self.fp16 else arr.float()
            model(arr)

    def __call__(self, orig_img: OrigImgs | OrigImg, conf_arg: ConfArgs | ConfArg | float = 0.25):
        """检测,流程为:前处理 --> 推理 --> 后处理

        Args:
            orig_img: 原始图像
            conf_arg: 置信度阈值,可以为float或list,当为list时,长度应与图像数量相同

        Returns:
            list[np.ndarray] | np.ndarray: 处理后的结果
        """

        model, device = self._get_device_model()
        is_one = not isinstance(orig_img, list)  # 判断是否为单张图像检测
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
        """
        预处理
        Args:
            ims: 图像列表
            device: 推理设备

        Returns:
            处理后的图像
        """

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

    def _postprocess(self, preds: torch.Tensor, *args):
        """
        后处理
        Args:
            preds: 模型预测结果
            args: 预处理参数

        Returns:
            处理后的结果
        """

        tensor_ims, orig_imgs, nms_args = args
        nms_args = nms_args if isinstance(nms_args, list) else [nms_args] * len(orig_imgs)
        processed_preds = []

        for pred, tensor_im, orig_img, nms_arg in zip(preds, tensor_ims, orig_imgs, nms_args):
            # 非极大值抑制nms处理
            processed_pred = ops.nms(pred, nms_arg)

            # boxes坐标恢复到原始图像
            processed_pred[..., :4] = ops.restore_scale(
                img1_shape=tensor_im.shape[-2:],
                boxes=processed_pred[..., :4],
                img0_shape=orig_img.shape[:2]
            )
            processed_preds.append(processed_pred.to('cpu').numpy())

        return processed_preds
