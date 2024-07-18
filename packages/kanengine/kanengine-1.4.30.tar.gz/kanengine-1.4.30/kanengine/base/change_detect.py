import torch
import torch.nn.functional as F
import numpy as np

from ..utils import AutoBackend
from ..abc import EngineABC


class BaseChangeDetect(EngineABC):

    def __init__(self, weight_path: str, device: int, fp16: bool = False):
        device = 'cpu' if device == -1 else f'cuda:{device}'
        self.model = AutoBackend(weight_path, device, fp16)
        self.device = device
        self.fp16 = fp16
        self.std = np.array([58.395, 57.12, 57.375, 58.395, 57.12, 57.375]).reshape(6, 1, 1)
        self.mean = np.array([123.675, 116.28, 103.53, 123.675, 116.28, 103.53,]).reshape(6, 1, 1)
        # self._warmup()

    def _warmup(self):
        for _ in range(10):
            arr = np.random.rand(1, 6, 1024, 1024).astype(np.float32)
            self.model(arr, to_torch=False, to_device=False)

    def __call__(self, img_A: np.ndarray, img_B: np.ndarray):
        input_data = self._preprocess(img_A, img_B)
        output_data = self._infer(input_data)
        pred = self._postprocess(output_data, img_A.shape[:2])

        return pred

    def _infer(self, input_data: np.ndarray):
        return self.model(input_data, to_torch=False, to_device=False)

    def _preprocess(self, img_A: np.ndarray, img_B: np.ndarray):
        im = np.concatenate([img_A, img_B], axis=2).transpose(2, 0, 1)
        im = (im - self.mean) / self.std
        im = np.expand_dims(im, axis=0)
        im = im.astype(np.float32)

        return im

    def _postprocess(self, output_data: np.ndarray, output_size: tuple = (1024, 1024)):
        pred = torch.from_numpy(output_data) if isinstance(output_data, np.ndarray) else output_data
        pred: torch.Tensor = F.interpolate(pred, size=output_size, mode='bilinear', align_corners=False)

        return pred
