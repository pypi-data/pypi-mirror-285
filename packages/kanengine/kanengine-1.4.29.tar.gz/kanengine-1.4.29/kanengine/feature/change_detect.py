"""变化检测"""

import cv2
import numpy as np
import torch
from torch.nn import functional as F
from shapely.geometry import Polygon

from ..base.change_detect import BaseChangeDetect


class ChangeDetector(BaseChangeDetect):

    @staticmethod
    def filter_contants_box(boxes):
        """过滤掉被包含在其他矩形框中的矩形框"""

        def is_contained(box1, box2):
            """判断box1是否被box2包含"""
            poly1 = Polygon(box1)
            poly2 = Polygon(box2)
            return poly1.within(poly2)

        result = []
        for i in range(len(boxes)):
            if not any(is_contained(boxes[i], boxes[j]) for j in range(len(boxes)) if i != j):
                result.append(boxes[i])
        return result

    def predict_and_plot(self, img_A: np.ndarray, img_B: np.ndarray, stride_size=(512, 512), crop_size=(1024, 1024)):
        h_stride, w_stride = stride_size
        h_crop, w_crop = crop_size
        h_img, w_img = img_A.shape[:2]
        h_grids = max(h_img - h_crop + h_stride - 1, 0) // h_stride + 1
        w_grids = max(w_img - w_crop + w_stride - 1, 0) // w_stride + 1
        pred_map = torch.zeros((1, 2, h_img, w_img))
        count_map = torch.zeros((1, 1, h_img, w_img))

        # 切分图像并检测单个区域的变化
        for h_idx in range(h_grids):
            for w_idx in range(w_grids):
                y1, x1 = h_idx * h_stride, w_idx * w_stride
                y2, x2 = min(y1 + h_crop, h_img), min(x1 + w_crop, w_img)
                y1, x1 = max(y2 - h_crop, 0), max(x2 - w_crop, 0)
                crop_A = img_A[y1:y2, x1:x2, :]
                crop_B = img_B[y1:y2, x1:x2, :]
                pred = super().__call__(crop_A, crop_B)
                x1_, x2_, y1_, y2_ = int(x1), int(pred_map.shape[3] - x2), int(y1), int(pred_map.shape[2] - y2)
                pad_arr = F.pad(pred, (x1_, x2_, y1_, y2_))
                pred_map += pad_arr
                count_map[:, :, y1:y2, x1:x2] += 1

        # 合并检测结果
        pred_map /= count_map
        pred_map = pred_map.argmax(dim=1).squeeze().numpy()
        pred_map = pred_map.astype(np.uint8)

        result_boxes = []
        pred_map = np.where(pred_map == 1, 255, 0).astype(np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        pred_map = cv2.morphologyEx(pred_map, cv2.MORPH_OPEN, kernel)  # 过滤很小的变化区域
        contours, _ = cv2.findContours(pred_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 计算矩形框
        for i in range(len(contours)):
            rect = cv2.minAreaRect(contours[i])
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            result_boxes.append(box)

        result_boxes = self.filter_contants_box(result_boxes)

        # 绘制矩形框
        for box in result_boxes:
            cv2.polylines(img_B, [box], True, (0, 255, 0), 6)

        return img_B, result_boxes

    def __call__(self, img_A: np.ndarray, img_B: np.ndarray):
        """检测图像变化并画出变化区域"""

        return self.predict_and_plot(img_A, img_B)
