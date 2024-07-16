import cv2
import numpy as np

from ..base.lane import BaseLaneDetector
from ..utils import ops
from ..register import ENGINES

__all__ = ['LaneDetector', 'FullLaneDetector']


@ENGINES.register()
class LaneDetector(BaseLaneDetector):
    """
    该车道线检测器实现以下功能:
    1. 求车道线宽度: 输入一张图片,输出车道线宽度(像素宽度)
    2. 判断点是否在检测的车道内: 输入一点坐标,判断该点是否在车道内
    """

    def __init__(self, weight_path, device: list[int], fp16=False, **kwargs):
        # TODO 适配多个GPU推理
        super().__init__(weight_path, fp16=fp16, device=device)
        self._left_func = None
        self._right_func = None
        self._lane_width = None

    def _fit_curve_func(self, lane: np.ndarray, img_w: int, img_h: int):
        points = []
        for k in range(len(lane)):
            value = lane[k]  # 车道线的点在哪一列
            if value > 0:
                x = value * self.col_sample_w
                y = self.row_anchor[18 - 1 - k]
                x = round(x * img_w / self.input_w) - 1
                y = round(y * img_h / self.input_h) - 1
                points.append((y, x))  # 将xy颠倒
        func = ops.fit_curve(points, 3)

        return func

    def predict(self, orig_img: np.ndarray):
        """车道线检测,返回车道宽度"""

        img_h, img_w = orig_img.shape[:2]
        pred = super().__call__(orig_img)

        # 过滤掉只有一点的车道线
        sum_per_colum = np.sum(pred != 0, axis=0)
        pred = pred[:, sum_per_colum >= 2]
        lane_num = pred.shape[1]

        # 拟合最左侧车道线和最右侧车道线
        left_func = self._fit_curve_func(pred[:, 0], img_w, img_h)
        right_func = self._fit_curve_func(pred[:, -1], img_w, img_h)

        # 取中间车道线,拟合
        half_right_lane = pred[:, lane_num // 2 - 1]
        half_right_func = self._fit_curve_func(half_right_lane, img_w, img_h)

        # 在左半边车道线上取三个预设点,计算到右半边车道线的距离,求平均
        preset_x = img_h // 4, img_h // 2, img_h * 3 // 4
        points = [(x, left_func(x)) for x in preset_x]
        distances = [ops.point_to_curve_distance(point, half_right_func) for point in points]
        left_road_width = np.mean(distances)
        lane_width = left_road_width / (lane_num // 2 - 1)

        # 将局部变量赋值给实例变量
        self._left_func = left_func
        self._right_func = right_func
        self._lane_width = lane_width

        return lane_width

    def __call__(self, img: np.ndarray):
        """车道线检测,返回车道宽度"""
        return self.predict(img)

    def is_in_lane(self, point: tuple | list):
        """判断点是否在车道内"""

        if self._left_func is None or self._right_func is None:
            return False

        y, x = point
        is_in = (self._left_func(x) - y) * (self._right_func(x) - y) < 0

        return is_in

    @property
    def lane_width(self):
        """车道宽度"""
        return self._lane_width


# TODO: 根据基础的车道线检测器，实现一个适用于其他场景的车道线检测器，包括车道线的拟合、车道线距离、车道线宽度等信息
class FullLaneDetector(BaseLaneDetector):
    def __init__(self, model_path, device='cuda:0', **kwargs):
        super().__init__(model_path, device, **kwargs)

    def __call__(self, img):
        img_h, img_w = img.shape[:2]
        pred = super().__call__(img)
        funcs = {}
        lane_num = pred.shape[1]
        row_anchor_num = pred.shape[0]

        for i in range(lane_num):
            points = []
            if np.sum(pred[:, i] != 0) < 2:
                continue
            for k in range(row_anchor_num):
                value = pred[k, i]  # 车道线的点在哪一列
                if value > 0:
                    x = value * self.col_sample_w
                    y = self.row_anchor[18 - 1 - k]
                    x = round(x * img_w / self.input_w) - 1
                    y = round(y * img_h / self.input_h) - 1
                    points.append((x, y))
            func = ops.fit_curve(points, 3)
            funcs[i] = func
            if len(points) > 1:
                cv2.polylines(img, [np.array(points)], False, (i*25, 0, 0), 2)

        return img, funcs
