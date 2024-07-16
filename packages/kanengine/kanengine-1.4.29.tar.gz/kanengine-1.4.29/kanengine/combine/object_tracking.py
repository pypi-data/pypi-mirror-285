import cv2
import numpy as np

from ..feature.detect import CommonDetector
from ..feature.obb_detect import CommonObbDetector
from ..base.trackers import BYTETracker
from ..utils import ops, plot
from ..abc import CombineEngineABC


class ObjectTracking(CombineEngineABC):

    def __init__(self, detector: CommonDetector, track_thresh=0.2, match_thresh=0.9):
        self.detector = detector
        self._tracker = BYTETracker(track_high_thresh=track_thresh, match_thresh=match_thresh)

    def __call__(self, orig_im: np.ndarray, option_area: dict | None = None, conf_args=0.25):

        h, w = orig_im.shape[:2]
        _orig_im = orig_im
        pts = None
        flag = False  # 判断是否过滤可选区域外的点

        if option_area:
            pts = np.array([option_area["x"], option_area["y"]]).T

            # 若点数不等于4或长宽不等于原始图像,则去ROI区域
            if len(pts) != 4 or np.sum(np.abs(pts[0] - pts[2]) + np.abs(pts[1] - pts[3])) != 4:
                flag = True
                pts[:, 0] = pts[:, 0] * w
                pts[:, 1] = pts[:, 1] * h
                pts = pts.astype(np.int32)
                mask = np.zeros_like(orig_im, dtype=np.uint8)
                cv2.fillPoly(mask, [pts], color=(255, 255, 255))
                _orig_im = cv2.bitwise_and(orig_im, mask)

        det_ret = self.detector.predict(_orig_im, conf_args=conf_args)
        det_ret[..., :4] = ops.xyxy2xywh(det_ret[..., :4])

        # 过滤可选区域外的点
        if flag and len(det_ret) > 0:
            mask = [ops.is_point_inside_polygon(ret[0], ret[1], pts) for ret in det_ret]
            det_ret = det_ret[mask, :]

        track_ret = self._tracker.update(det_ret, None)
        res_pts = {}
        plotted_im = orig_im.copy() if len(track_ret) else orig_im
        for *box, id_, conf, cls, ind in track_ret:
            plot.plot_box(plotted_im, box, color=(0, 255, 50), box_format="xywh")
            x, y = int(box[0]), int(box[1])
            res_pts[int(id_)] = (x / w, y / h)

        return plotted_im, res_pts


class ObbTracking(CombineEngineABC):

    def __init__(self, detector: CommonObbDetector, track_thresh=0.2, match_thresh=0.9):
        self.detector = detector
        self._tracker = BYTETracker(track_high_thresh=track_thresh, match_thresh=match_thresh)

    def __call__(self, orig_im: np.ndarray, conf_args=None):
        h, w = orig_im.shape[:2]
        _orig_im = orig_im

        det_ret = self.detector.predict(_orig_im, conf_args=conf_args)

        track_ret = self._tracker.update(det_ret, None)
        res_pts = {}
        plotted_im = orig_im.copy() if len(track_ret) else orig_im
        for *box, id_, conf, cls, ind in track_ret:
            plot.plot_box_by_xywha(plotted_im, box, color=(0, 255, 50))
            x, y = box[0], box[1]
            res_pts[id_] = (x / w, y / h)

        return plotted_im, res_pts
