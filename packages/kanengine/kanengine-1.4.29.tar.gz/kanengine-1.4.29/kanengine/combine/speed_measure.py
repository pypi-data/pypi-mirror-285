from collections import defaultdict

import numpy as np

from ..base.detect import BaseDetector
from ..base.trackers import BYTETracker
from ..base.lane2 import BaseLaneDetector
from ..utils import plot
from ..abc import CombineEngineABC


class SpeedMeasure(CombineEngineABC):

    def __init__(self, vehicle_detector: BaseDetector, lane_detector: BaseLaneDetector):
        self._vehicle_detector = vehicle_detector
        self._lane_detector = lane_detector
        self._tracker = BYTETracker()
        self._real_lane_width = 3.75
        self._time_interval = 0  # 前后两帧的时间差
        self._base_speed = 0  # 基准速度
        self._objects = defaultdict(tuple)
        self._lane_num = 8

    def _measure(self, track_ret: np.ndarray, lane_ret):
        measure_results = {i: [] for i in range(1, len(lane_ret))}
        for *box, id_, conf, cls, ind in track_ret:
            x1, y1 = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2

            if id_ not in self._objects:
                self._objects[id_] = x1, y1
                continue

            # 判断所属车道
            lane_id, lane_width = self._belong_lane((x1, y1), lane_ret)

            # 如果车辆不在车道内，则过滤
            if lane_id == -1:
                continue

            rate = self._real_lane_width / lane_width
            x2, y2 = self._objects[id_]
            distance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            virtual_speed = distance / self._time_interval
            sign = -1 if y1 - y2 > 0 else 1
            real_speed = sign * virtual_speed * rate + self._base_speed
            self._objects[id_] = x1, y1
            measure_results[lane_id].append((box, id_, conf, cls, real_speed))

        return measure_results

    @staticmethod
    def _belong_lane(point, lane_ret: dict):
        """判断某个点属于哪个车道内"""

        y0, x0 = point
        lane_num = len(lane_ret) - 1

        for index, lane in lane_ret.items():
            pre_func, next_func = lane['curve_func']
            condition = (pre_func(x0) - y0) * (next_func(x0) - y0)
            if condition <= 0 and index != lane_num // 2:
                index = index + 1 if index < lane_num // 2 else index
                return index, lane['lane_width']

        return -1, 0

    def __call__(self, img: np.ndarray, base_speed: float, time_interval: float = 1 / 30):
        self._base_speed = base_speed
        self._time_interval = time_interval
        vehicle_ret = self._vehicle_detector(img)
        track_ret = self._tracker.update(vehicle_ret, None)
        lane_det = self._lane_detector(img)

        measure_results = self._measure(track_ret, lane_det)
        # TODO
        plotted_img = plot.plot_highway(img, measure_results, self._names, lane_det)

        return plotted_img
