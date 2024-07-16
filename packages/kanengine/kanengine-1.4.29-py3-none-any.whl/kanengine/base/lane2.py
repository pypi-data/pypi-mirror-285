# TODO:作为参考，之后需要修改成适合的版本

"""
车道线检测器
"""

import time

import cv2
import torch
import numpy as np
import torch.nn.functional as F
from scipy import optimize

from ..abc import EngineABC

WEIGHT_PATH = 'D:/PycharmProject/Ultra-Fast-Lane-Detection/UFLD.torchscript-cuda.pt'
GRIDING_NUM = 200
ANCHORS = 18
INPUT_H, INPUT_W = 288, 512


def fit_curve(points: list, degree=3):
    if len(points) == 0:
        return None

    points = np.array(points)
    coefficients = np.polyfit(points[:, 1], points[:, 0], degree)
    func = np.poly1d(coefficients)

    return func


"""
    'Nelder-Mead' (see here)  
    'Powell' (see here)  
    'CG' (see here)  
    'BFGS' (see here)  
    'Newton-CG' (see here)  
    'L-BFGS-B' (see here)  
    'TNC' (see here)  
    'COBYLA' (see here)  
    'SLSQP' (see here)  
    'trust-constr'(see here)  
    'dogleg' (see here)  
    'trust-ncg' (see here)  
    'trust-exact' (see here)  
    'trust-krylov' (see here)  
"""


def calculate_distance(point, func):
    x0, y0 = point
    initial_guess = np.asarray((x0))
    optimized_func = lambda x: ((func(x) - y0) ** 2 + (x - x0) ** 2) ** 0.5
    result = optimize.minimize(optimized_func, initial_guess, method='COBYLA')

    distance = result.fun

    return distance


class BaseLaneDetector(EngineABC):

    def __init__(self, weight_path: str, device='cuda:0') -> None:
        model = torch.jit.load(weight_path, map_location=device)
        model.eval()
        self.model = model
        self.device = device
        self.input_h = INPUT_H
        self.input_w = INPUT_W
        self.anchors = ANCHORS
        self.griding_num = GRIDING_NUM
        col_sample = np.linspace(0, INPUT_W - 1, GRIDING_NUM)
        self.col_sample_w = col_sample[1] - col_sample[0]
        self.row_anchor = list(np.linspace(1, INPUT_H - 1, ANCHORS, dtype=np.uint16))
        self._warmup()

    def _warmup(self):
        arr = torch.zeros((1, 3, self.input_h, self.input_w), device=self.device)
        for _ in range(45):
            self.model(arr)

    def _preprocess(self, img: np.ndarray, input_w=512, input_h=288) -> torch.Tensor:
        img = cv2.resize(img, (input_w, input_h), interpolation=cv2.INTER_LINEAR)
        img_t = torch.tensor(img, dtype=torch.float32, device=self.device).permute(2, 0, 1) / 255
        mean = torch.tensor((0.406, 0.456, 0.485), device=self.device).view(3, 1, 1)
        std = torch.tensor((0.225, 0.224, 0.229), device=self.device).view(3, 1, 1)
        img_t = (img_t - mean) / std
        img_t = img_t.flip(0)
        img_ = img_t.unsqueeze(0)

        return img_

    def _infer(self, img: torch.Tensor):
        img = img.cuda()
        with torch.no_grad():
            pred = self.model(img)

        return pred

    def _postprocess(self, pred: torch.Tensor, img_w=1920, img_h=1080):
        col_sample_w = self.col_sample_w
        griding_num = self.griding_num
        input_w = self.input_w
        input_h = self.input_h
        anchors = self.anchors
        row_anchor = self.row_anchor

        # reformat结果
        out_j = pred[0].flip(1)
        prob = F.softmax(out_j[:-1, :, :], dim=0)
        idx = torch.arange(griding_num, device=self.device) + 1
        idx = idx.view(-1, 1, 1)
        loc = torch.sum(prob * idx, dim=0)
        out_j = torch.argmax(out_j, dim=0)
        loc[out_j == griding_num] = 0
        out_j = loc.cpu().numpy()

        # 还原尺寸,并拟合曲线
        ret = {}
        for i in range(out_j.shape[1]):
            # ret[i] = None
            points = []
            if np.sum(out_j[:, i] != 0) < 2:
                continue
            for k in range(out_j.shape[0]):
                value = out_j[k, i]
                if value > 0:
                    x = value * col_sample_w
                    y = row_anchor[anchors - 1 - k]
                    x = round(x * img_w / input_w) - 1
                    y = round(y * img_h / input_h) - 1
                    points.append((x, y))
            func = fit_curve(points, 3)
            ret[i] = func
            # ret[i] = {'points': points, 'funcs': func}

        # 车道线排序,并计算车道的像素宽度
        ret = sorted(ret.values(), key=lambda func: func(img_h / 2))

        preset_x = list(range(img_h // 5, img_h * 4 // 5, img_h * 3 // 5 // 3))
        # t4 = time.time()
        ret_ = {}
        dts = 0
        for i in range(len(ret) - 1):
            pre_func = ret[i]
            next_func = ret[i + 1]
            points = [(x, pre_func(x)) for x in preset_x]
            t1 = time.time()
            distances = [calculate_distance(point, next_func) for point in points]
            dts += (time.time() - t1)
            lane_width = np.mean(distances)
            ret_[i] = {'lane_width': lane_width, 'curve_func': (pre_func, next_func)}

        # logger.warning(f'width:{(time.time() - t4) * 1000:.1f}ms,dts:{dts * 1000:.1f}ms')

        return ret_

    def __call__(self, orig_im: np.ndarray):
        tensor_im = self._preprocess(orig_im)
        pred = self._infer(tensor_im)
        processed_pred = self._postprocess(pred, img_h=orig_im.shape[0], img_w=orig_im.shape[1])

        return processed_pred
