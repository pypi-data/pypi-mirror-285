"""人流量检测"""

import cv2
import numpy as np

from ..base.people_flow import BasePeopleFlowDetect
from ..utils import ops, plot
from ..register import ENGINES


@ENGINES.register()
class PeopleFlowDetect(BasePeopleFlowDetect):

    def predict_and_plot(self, orig_img: np.ndarray, threshold=0.3, option_area: dict | None = None, **kwargs):
        h, w = orig_img.shape[:2]
        _orig_img = orig_img
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
                mask = np.zeros_like(orig_img, dtype=np.uint8)
                cv2.fillPoly(mask, [pts], color=(255, 255, 255))
                _orig_img = cv2.bitwise_and(orig_img, mask)

        # 执行推理
        pred_pts = super().__call__(_orig_img, threshold)
        pred_pts = pred_pts.astype(np.int32)

        # 过滤可选区域外的点
        if flag and len(pred_pts) > 0:
            mask = [ops.is_point_inside_polygon(pt[0], pt[1], pts) for pt in pred_pts]
            pred_pts = pred_pts[mask, :]

        # 绘制点
        plotted_im = plot.plot_dots(orig_img.copy(), pred_pts)
        if len(pred_pts):
            x_list = (pred_pts[:, 0] / w).tolist()
            y_list = (pred_pts[:, 1] / h).tolist()
            res_pts = {'x': x_list, 'y': y_list}
        else:
            res_pts = {'x': [], 'y': []}

        return plotted_im, res_pts

    def __call__(self, orig_img: np.ndarray, threshold=0.3, option_area: dict | None = None, **kwargs):
        return self.predict_and_plot(orig_img, threshold, option_area, **kwargs)
