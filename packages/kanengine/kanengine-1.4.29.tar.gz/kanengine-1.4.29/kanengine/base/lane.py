"""车道线检测"""

import cv2
import torch
import numpy as np
import torch.nn.functional as F

from ..abc import EngineABC
from ..utils import AutoBackend


class BaseLaneDetector(EngineABC):

    def __init__(self, weight_path: str, device: list[int], fp16=False, input_size=(288, 800)):
        device = f'cuda:{device[0]}'
        model = AutoBackend(weight_path, device=device, fp16=fp16)  # TODO:适配多个GPU推理
        self.model = model
        self.input_h, self.input_w = input_size
        self.device = device
        col_sample = np.linspace(0, self.input_w - 1, 200)
        self.col_sample_w = col_sample[1] - col_sample[0]
        self.row_anchor = list(np.linspace(1, self.input_h - 1, 18, dtype=np.uint16))
        self._warmup()

    def _warmup(self, *args, **kwargs):
        arr = torch.zeros((1, 3, self.input_h, self.input_w))
        for _ in range(45):
            self.model(arr)

    def _preprocess(self, img: np.ndarray):
        img = cv2.resize(img, (self.input_w, self.input_h), interpolation=cv2.INTER_LINEAR)
        img_t = torch.tensor(img, dtype=torch.float32, device=self.device).permute(2, 0, 1) / 255
        mean = torch.tensor((0.406, 0.456, 0.485), device=self.device).view(3, 1, 1)
        std = torch.tensor((0.225, 0.224, 0.229), device=self.device).view(3, 1, 1)
        img_t = (img_t - mean) / std
        img_t = img_t.flip(0)
        img_ = img_t.unsqueeze(0)

        return img_

    def _infer(self, img):
        return self.model(img)

    def _postprocess(self, pred: torch.Tensor):
        with torch.no_grad():
            out_j = pred[0].flip(1)
            prob = F.softmax(out_j[:-1, :, :], dim=0)
            idx = torch.arange(200, device=self.device) + 1
            idx = idx.view(-1, 1, 1)
            loc = torch.sum(prob * idx, dim=0)
            out_j = torch.argmax(out_j, dim=0)
            loc[out_j == 200] = 0
            out_j = loc.cpu().numpy()

        return out_j

    def __call__(self, orig_img: np.ndarray):
        tensor_im = self._preprocess(orig_img)
        pred = self._infer(tensor_im)
        final_pred = self._postprocess(pred)

        return final_pred
