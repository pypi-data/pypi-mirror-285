import numpy as np

from ..feature import CommonObbDetector, LaneDetector
from ..base.trackers import BYTETracker
from ..abc import CombineEngineABC
from ..utils import plot


class AccidentDetector(CombineEngineABC):
    def __init__(self, lane_detector: LaneDetector, obb_detector: CommonObbDetector):
        self._byte_tracker = BYTETracker()
        self._lane_detector = lane_detector
        self._vehicle_detector = obb_detector
        self._history_coord = {}  # 历史坐标
        self._real_lane_width = 3.75  # 车道真实宽度
        self._resting_v = 3  # 静止速度的范围,若速度在-3到3之间则判定为静止
        self._lane_width = 0  # 车道像素宽度
        self._base_speed = 0  # 基础速度
        self._time_interval = 0  # 时间间隔

    def _filter_in_lane(self, det_rets: np.ndarray):
        """过滤出车辆在车道内的坐标"""

        new_rets = []
        for x, y, *other in det_rets:
            if self._lane_detector.is_in_lane((x, y)):
                new_rets.append((x, y, *other))
        return np.array(new_rets)

    def _detect_accident(self, track_rets: np.ndarray, img_h: int, img_w: int):
        accident_rets = np.array([])  # 事故车辆坐标
        new_rets = []  # 所有车辆坐标,包括速度
        for *box, id_, conf, cls, ind in track_rets:
            x, y, w, h, angle = box

            # 若历史坐标中没有该id,则添加,且不进行速度测量
            if id_ not in self._history_coord:
                self._history_coord[id_] = x, y
                continue

            # 如果车辆不在车道内，则过滤
            # if not self._lane_detector.is_in_lane((x, y)):
            #     continue

            # 计算速度
            gsd = self._real_lane_width / self._lane_width
            x0, y0 = self._history_coord[id_]  # 获取历史坐标
            distance = ((x0 - x) ** 2 + (y0 - y) ** 2) ** 0.5  # 计算两点距离
            virtual_speed = distance / self._time_interval  # 计算画面像素速度
            sign = -1 if y - y0 > 0 else 1  # 计算方向
            real_speed = sign * virtual_speed * gsd + self._base_speed * np.abs(np.sin(angle))  # 计算真实速度
            self._history_coord[id_] = x, y  # 更新历史坐标
            new_rets.append((*box, id_, conf, cls, real_speed))

        # 若没有车辆,则直接返回空
        if len(new_rets) == 0:
            return None, new_rets

        new_rets = np.array(new_rets)
        # 若速度在静止速度范围内则将速度置为0
        new_rets[:, -1][(new_rets[:, -1] > -self._resting_v) & (new_rets[:, -1] < self._resting_v)] = 0
        # 统计速度为0的个数
        zero_rets = new_rets[new_rets[:, -1] == 0, :]
        zero_count = len(zero_rets)

        # 若存在10个以下速度为0的车辆,且在图像中央存在速度为0的车辆,则取画面所有速度为0的车辆视为事故车辆
        if 0 < zero_count < 10:
            # 提取y坐标在四分之一到四分至三图像高度内的车辆
            y_min = img_h // 4
            y_max = img_h * 3 // 4
            mid_rets = new_rets[(new_rets[:, 1] > y_min) & (new_rets[:, 1] < y_max), :]
            # 统计在图像中央的速度为0的车辆个数
            mid_zero_count = np.sum(mid_rets[:, -1] == 0)

            # 若在图像中央的速度为0的车辆个数大于0,则画面所有速度为0的车辆视为事故车辆
            if mid_zero_count > 0:
                accident_rets = zero_rets

        return accident_rets, new_rets

    @staticmethod
    def plot_with_speed(img: np.ndarray, rets: None | np.ndarray):
        """绘制图像及速度"""

        if rets is None or len(rets) == 0:
            return img

        line_width = max(round(sum(img.shape) / 2 * 0.003), 2)
        for *box, id_, conf, cls, speed in rets:
            speed = speed * 3.6
            label = f'{speed:.1f}km/h'
            if speed == 0:
                color = (0, 0, 255)
            elif abs(speed) > 130:
                color = (0, 140, 255)
            else:
                color = (255, 0, 0)
            img = plot.plot_box_by_xywha(img, box, label=label, color=color, line_width=line_width, text_thickness=2)

        return img

    def predict(self, img, base_speed=5, time_interval=0.033, open_track=False, open_lane=False):
        self._base_speed = base_speed
        self._time_interval = time_interval
        if open_lane:
            self._lane_width = self._lane_detector.predict(orig_img=img)

        if open_track:
            # 车辆检测
            vehicle_rets = self._vehicle_detector.predict(orig_img=img)
            # 过滤出车辆在车道内的坐标
            vehicle_rets = self._filter_in_lane(det_rets=vehicle_rets)

            # 若没有车辆,则直接返回空
            if len(vehicle_rets) == 0:
                return None, vehicle_rets

            # 若有车辆,则进行车辆跟踪并检测事故车辆
            track_rets = self._byte_tracker.update(det_rets=vehicle_rets)  # 车辆跟踪

            # 若没有跟踪到车辆,则直接返回空
            if len(track_rets) == 0:
                return None, track_rets

            # 若有跟踪到车辆,则进行事故车辆检测
            accident_rets, new_rets = self._detect_accident(track_rets, *img.shape[:2])
            return accident_rets, new_rets

        return None, None
