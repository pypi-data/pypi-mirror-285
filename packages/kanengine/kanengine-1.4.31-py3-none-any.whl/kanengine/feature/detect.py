"""通用目标检测"""

from typing import TypeAlias
from collections.abc import Generator

import numpy as np

from ..utils import plot, ops
from ..register import ENGINES
from ..base.detect import BaseDetector

YieldType: TypeAlias = tuple[np.ndarray, list]
SendType: TypeAlias = tuple[np.ndarray, dict]
DetectGenerator: TypeAlias = Generator[YieldType, SendType, None]


@ENGINES.register()
class CommonDetector(BaseDetector):
    """通用目标检测"""

    def __init__(
            self, weight_path: str, device: list[int], fp16=True,
            classes: dict[int, str] = None, input_size=(640, 640), interval=1, **kwargs
    ):
        super().__init__(weight_path, device, fp16, input_size)
        self.classes = classes if classes else {i: str(i) for i in range(80)}
        self.interval = interval

    def _plot(self, orig_img: np.ndarray, pred: np.ndarray):
        plotted_img = orig_img.copy() if len(pred) else orig_img  # 若有预测结果,则复制一份原始图片,否则直接使用原图
        line_width = max(round(sum(orig_img.shape) / 2 * 0.003), 2)
        for *box, conf, cls in pred:
            cls = int(cls)
            label_name = self.classes[cls]
            color = plot.choose_color(cls)
            plotted_img = plot.plot_box_by_xyxy(
                image=plotted_img, box=box,
                label=label_name, color=color[::-1],
                line_width=line_width, return_pts=False
            )

        return plotted_img

    def predict_different_conf(self, orig_img: np.ndarray,
                               conf_args: dict[int, float] | float = 0.25) -> DetectGenerator:
        """根据置信度阈值,输出不同置信度的检测结果"""

        pred: np.ndarray = super().__call__(orig_img, conf_args)
        result = None

        while True:
            item = yield result
            orig_img, conf_arg = item
            mask = np.isin(pred[:, -1], list(conf_arg.keys()))
            _pred = pred[mask]
            plotted_img = self._plot(orig_img, _pred)
            result = _pred, plotted_img

    def predict(self, orig_img: np.ndarray, conf_args: dict[int, float] | float = 0.25):
        """调用子类预测函,仅输出检测结果,不绘制检测框,供组合算法调用"""

        pred: np.ndarray = super().__call__(orig_img, conf_args)

        return pred

    def predict_and_plot(self, orig_img: np.ndarray, conf_arg: dict[int, float] | float = 0.25):
        """
        预测并绘制检测框
        Returns:
            pred: 预测结果,包含(x1, y1, x2, y2, x3, y3, x4, y4, conf, cls)
            plotted_img: 绘制了检测框的图片
        """

        pred: np.ndarray = super().__call__(orig_img, conf_arg)  # 调用子类进行推理
        plotted_img = self._plot(orig_img, pred)  # 绘制检测框
        expanded_boxes = ops.xyxy2xyxyxyxy(pred[..., :-2])
        pred = np.concatenate((expanded_boxes, pred[..., -2:]), axis=-1)

        return pred, plotted_img

    def __call__(self, orig_img: np.ndarray, conf_arg: dict[int, float] | float = 0.25):
        """
        预测并绘制检测框
        Returns:
            pred: 预测结果,包含(x1, y1, x2, y2, x3, y3, x4, y4, conf, cls)
            plotted_img: 绘制了检测框的图片
        """

        return self.predict_and_plot(orig_img, conf_arg)
