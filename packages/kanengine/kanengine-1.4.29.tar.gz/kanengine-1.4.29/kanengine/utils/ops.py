"""处理工具模块"""

import math

import cv2
import numpy as np
import torch
import torchvision
from scipy import optimize


def clip_boxes(boxes, shape):
    """
    将一个边界框列表和一个形状（高度，宽度），对边界框进行裁剪。

    参数:
        boxes (torch.Tensor): 需要裁剪的边界框
        shape (tuple): 图像的形状

    返回:
        (torch.Tensor | numpy.ndarray): 裁剪后的边界框
    """

    if isinstance(boxes, torch.Tensor):  # faster individually (WARNING: inplace .clamp_() Apple MPS bug)
        boxes[..., 0] = boxes[..., 0].clamp(0, shape[1])  # x1
        boxes[..., 1] = boxes[..., 1].clamp(0, shape[0])  # y1
        boxes[..., 2] = boxes[..., 2].clamp(0, shape[1])  # x2
        boxes[..., 3] = boxes[..., 3].clamp(0, shape[0])  # y2
    else:  # np.array (faster grouped)
        boxes[..., [0, 2]] = boxes[..., [0, 2]].clip(0, shape[1])  # x1, x2
        boxes[..., [1, 3]] = boxes[..., [1, 3]].clip(0, shape[0])  # y1, y2
    return boxes


def scale_boxes(img1_shape, boxes, img0_shape, ratio_pad=None, padding=True, xywh=False):
    """
    将边界框（默认为xyxy格式）从它们最初指定的图像形状（img1_shape）重新调整到不同图像的形状（img0_shape）。

    参数:
        img1_shape（元组）：边界框所属图像的形状，格式为（高度，宽度）。
        boxes（torch.Tensor）：图像中物体的边界框，格式为（x1，y1，x2，y2）。
        img0_shape（元组）：目标图像的形状，格式为（高度，宽度）。
        ratio_pad（元组）：用于缩放边界框的比例和填充值（ratio，pad）。如果未提供，则将根据两个图像之间的大小差异计算比例和填充值。
        padding（布尔值）：如果为True，则假设边界框基于通过yolo风格增强的图像。如果为False，则进行常规重新调整。
        xywh（布尔值）：边界框格式是否为xywh，默认为False。

    返回:
        boxes（torch.Tensor）：缩放后的边界框，格式为（x1，y1，x2，y2）。
    """

    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (
            round((img1_shape[1] - img0_shape[1] * gain) / 2 - 0.1),
            round((img1_shape[0] - img0_shape[0] * gain) / 2 - 0.1),
        )  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    if padding:
        boxes[..., 0] -= pad[0]  # x padding
        boxes[..., 1] -= pad[1]  # y padding
        if not xywh:
            boxes[..., 2] -= pad[0]  # x padding
            boxes[..., 3] -= pad[1]  # y padding
    boxes[..., :4] /= gain
    return clip_boxes(boxes, img0_shape)


def regularize_rboxes(rboxes):
    """
    将旋转框规范化到区间[0, pi/2]。

    Args:
        rboxes (torch.Tensor): (N, 5), xywhr.

    Returns:
        (torch.Tensor): 规范化后的框。
    """

    x, y, w, h, t = rboxes.unbind(dim=-1)
    # Swap edge and angle if h >= w
    w_ = torch.where(w > h, w, h)
    h_ = torch.where(w > h, h, w)
    t = torch.where(w > h, t, t + math.pi / 2) % math.pi
    return torch.stack([x, y, w_, h_, t], dim=-1)  # regularized boxes


def convert_torch2numpy_batch(batch: torch.Tensor) -> np.ndarray:
    """
    将一批FP32的torch张量（0.0-1.0）转换为NumPy uint8数组（0-255），并将布局从BCHW更改为BHWC。

    Args:
        batch (torch.Tensor): 输入张量批次，形状为（Batch，Channels，Height，Width），数据类型为torch.float32。

    Returns:
        (np.ndarray): 输出NumPy数组批次，形状为（Batch，Height，Width，Channels），数据类型为uint8。
    """

    return (batch.permute(0, 2, 3, 1).contiguous() * 255).clamp(0, 255).to(torch.uint8).cpu().numpy()


def _get_covariance_matrix(boxes):
    """
    从旋转边界框生成协方差矩阵。

    Args:
        boxes (torch.Tensor): 形状为（N，5）的张量，表示旋转边界框，采用xywhr格式。

    Returns:
        (torch.Tensor): 对应于原始旋转边界框的协方差矩阵。
    """

    # 高斯边界框，忽略中心点（前两列），因为这里不需要它们。
    gbbs = torch.cat((boxes[:, 2:4].pow(2) / 12, boxes[:, 4:]), dim=-1)
    a, b, c = gbbs.split(1, dim=-1)
    cos = c.cos()
    sin = c.sin()
    cos2 = cos.pow(2)
    sin2 = sin.pow(2)
    return a * cos2 + b * sin2, a * sin2 + b * cos2, (a - b) * cos * sin


def batch_probiou(obb1, obb2, eps=1e-7):
    """
    计算定向边界框之间的IoU概率，参考论文链接: https://arxiv.org/pdf/2106.06072v1.pdf。

    参数:
        obb1 (torch.Tensor | np.ndarray): 表示实际定向边界框的形状为 (N, 5) 的张量，采用xywhr格式。
        obb2 (torch.Tensor | np.ndarray): 表示预测定向边界框的形状为 (M, 5) 的张量，采用xywhr格式。
        eps (float, optional): 一个避免除以零的小值。默认为1e-7。

    返回:
        (torch.Tensor): 表示obb相似性的形状为 (N, M) 的张量。
    """

    obb1 = torch.from_numpy(obb1) if isinstance(obb1, np.ndarray) else obb1
    obb2 = torch.from_numpy(obb2) if isinstance(obb2, np.ndarray) else obb2

    x1, y1 = obb1[..., :2].split(1, dim=-1)
    x2, y2 = (x.squeeze(-1)[None] for x in obb2[..., :2].split(1, dim=-1))
    a1, b1, c1 = _get_covariance_matrix(obb1)
    a2, b2, c2 = (x.squeeze(-1)[None] for x in _get_covariance_matrix(obb2))

    t1 = (
        ((a1 + a2) * (y1 - y2).pow(2) + (b1 + b2) * (x1 - x2).pow(2)) / (
            (a1 + a2) * (b1 + b2) - (c1 + c2).pow(2) + eps)
    ) * 0.25
    t2 = (((c1 + c2) * (x2 - x1) * (y1 - y2)) / ((a1 + a2) * (b1 + b2) - (c1 + c2).pow(2) + eps)) * 0.5
    t3 = (
        ((a1 + a2) * (b1 + b2) - (c1 + c2).pow(2))
        / (4 * ((a1 * b1 - c1.pow(2)).clamp_(0) * (a2 * b2 - c2.pow(2)).clamp_(0)).sqrt() + eps)
        + eps
    ).log() * 0.5
    bd = (t1 + t2 + t3).clamp(eps, 100.0)
    hd = (1.0 - (-bd).exp() + eps).sqrt()
    return 1 - hd


def nms_rotated(boxes, scores, threshold=0.45):
    """
    由 probiou 和 fast-nms 提供支持的 obbs 的 NMS。

    Args:
        boxes (torch.Tensor): (N, 5), xywhr。
        scores (torch.Tensor): (N, )。
        threshold (float): IoU 阈值。

    Returns:
    """

    if len(boxes) == 0:
        return np.empty((0,), dtype=np.int8)
    sorted_idx = torch.argsort(scores, descending=True)
    boxes = boxes[sorted_idx]
    ious = batch_probiou(boxes, boxes).triu_(diagonal=1)
    pick = torch.nonzero(ious.max(dim=0)[0] < threshold).squeeze_(-1)
    return sorted_idx[pick]


def non_max_suppression(
        prediction,
        conf_thres=0.25,
        iou_thres=0.45,
        classes=None,
        agnostic=False,
        multi_label=False,
        labels=(),
        max_nms=30000,
        max_wh=7680,
        in_place=True,
        rotated=False,
):
    bs = prediction.shape[0]  # batch size
    nc = prediction.shape[1] - 5 if rotated else prediction.shape[1] - 4
    nm = prediction.shape[1] - nc - 4
    mi = 4 + nc  # mask start index
    xc = prediction[:, 4:mi].amax(1) > conf_thres  # candidates

    # Settings
    # min_wh = 2  # (pixels) minimum box width and height
    multi_label &= nc > 1  # multiple labels per box (adds 0.5ms/img)

    prediction = prediction.transpose(-1, -2)  # shape(1,84,6300) to shape(1,6300,84)
    if not rotated:
        if in_place:
            prediction[..., :4] = xywh2xyxy(prediction[..., :4])  # xywh to xyxy
        else:
            prediction = torch.cat((xywh2xyxy(prediction[..., :4]), prediction[..., 4:]), dim=-1)  # xywh to xyxy

    output = [torch.zeros((0, 6 + nm), device=prediction.device)] * bs
    for xi, x in enumerate(prediction):  # image index, image inference
        # Apply constraints
        # x[((x[:, 2:4] < min_wh) | (x[:, 2:4] > max_wh)).any(1), 4] = 0  # width-height
        x = x[xc[xi]]  # confidence

        # Cat apriori labels if autolabelling
        if labels and len(labels[xi]) and not rotated:
            lb = labels[xi]
            v = torch.zeros((len(lb), nc + nm + 4), device=x.device)
            v[:, :4] = xywh2xyxy(lb[:, 1:5])  # box
            v[range(len(lb)), lb[:, 0].long() + 4] = 1.0  # cls
            x = torch.cat((x, v), 0)

        # If none remain process next image
        if not x.shape[0]:
            continue

        # Detections matrix nx6 (xyxy, conf, cls)
        box, cls, mask = x.split((4, nc, nm), 1)

        if multi_label:
            i, j = torch.where(cls > conf_thres)
            x = torch.cat((box[i], x[i, 4 + j, None], j[:, None].float(), mask[i]), 1)
        else:  # best class only
            conf, j = cls.max(1, keepdim=True)
            x = torch.cat((box, conf, j.float(), mask), 1)[conf.view(-1) > conf_thres]

        # Filter by class
        if classes is not None:
            x = x[(x[:, 5:6] == torch.tensor(classes, device=x.device)).any(1)]

        # Check shape
        n = x.shape[0]  # number of boxes
        if not n:  # no boxes
            continue
        if n > max_nms:  # excess boxes
            x = x[x[:, 4].argsort(descending=True)[:max_nms]]  # sort by confidence and remove excess boxes

        # Batched NMS
        c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
        scores = x[:, 4]  # scores
        if rotated:
            boxes = torch.cat((x[:, :2] + c, x[:, 2:4], x[:, -1:]), dim=-1)  # xywhr
            i = nms_rotated(boxes, scores, iou_thres)
        else:
            boxes = x[:, :4] + c  # boxes (offset by class)
            i = torchvision.ops.nms(boxes, scores, iou_thres)  # NMS

        output[xi] = x[i]

    return output


def probiou(obb1, obb2, CIoU=False, eps=1e-7):
    """
    计算定向边界框之间的IoU概率，https://arxiv.org/pdf/2106.06072v1.pdf。

    Args:
        obb1 (torch.Tensor): 形状为(N, 5)的张量，表示带有xywhr格式的真实边界框。
        obb2 (torch.Tensor): 形状为(N, 5)的张量，表示带有xywhr格式的预测边界框。
        eps (float, optional): 一个小值，用于避免除以零。默认值为1e-7。

    Returns:
        (torch.Tensor): 形状为(N, )的张量，表示边界框相似性。
    """

    x1, y1 = obb1[..., :2].split(1, dim=-1)
    x2, y2 = obb2[..., :2].split(1, dim=-1)
    a1, b1, c1 = _get_covariance_matrix(obb1)
    a2, b2, c2 = _get_covariance_matrix(obb2)

    t1 = (
        ((a1 + a2) * (y1 - y2).pow(2) + (b1 + b2) * (x1 - x2).pow(2)) / (
            (a1 + a2) * (b1 + b2) - (c1 + c2).pow(2) + eps)
    ) * 0.25
    t2 = (((c1 + c2) * (x2 - x1) * (y1 - y2)) / ((a1 + a2) * (b1 + b2) - (c1 + c2).pow(2) + eps)) * 0.5
    t3 = (
        ((a1 + a2) * (b1 + b2) - (c1 + c2).pow(2))
        / (4 * ((a1 * b1 - c1.pow(2)).clamp_(0) * (a2 * b2 - c2.pow(2)).clamp_(0)).sqrt() + eps)
        + eps
    ).log() * 0.5
    bd = (t1 + t2 + t3).clamp(eps, 100.0)
    hd = (1.0 - (-bd).exp() + eps).sqrt()
    iou = 1 - hd
    if CIoU:  # only include the wh aspect ratio part
        w1, h1 = obb1[..., 2:4].split(1, dim=-1)
        w2, h2 = obb2[..., 2:4].split(1, dim=-1)
        v = (4 / math.pi ** 2) * ((w2 / h2).atan() - (w1 / h1).atan()).pow(2)
        with torch.no_grad():
            alpha = v / (v - iou + (1 + eps))
        return iou - v * alpha  # CIoU
    return iou


def adjust_scale(img: np.ndarray, new_shape: tuple = (640, 640)):
    shape = img.shape[:2]

    # 根据原图的高宽比计算新的高宽
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))

    # 缩放原图至新的高宽
    if shape[::-1] != new_unpad:
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)

    # 计算边缘的宽和高
    dw = (new_shape[1] - new_unpad[0]) / 2
    dh = (new_shape[0] - new_unpad[1]) / 2

    # 拓展边缘
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114))

    return img


def restore_scale(img1_shape: torch.Size, boxes: torch.Tensor, img0_shape: tuple):
    """将检测框从推理的输入图中映射到原始图像中

    Parameters
    ----------
    img1_shape : torch.Size
        推理的输入图的性状(hw)
    boxes : torch.Tensor
        nms过后的检测框(xyxy)
    img0_shape : tuple
        原始图的性状(hw)

    Returns
    -------
    _type_
        _description_
    """
    gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])
    pad = round((img1_shape[1] - img0_shape[1] * gain) / 2 - 0.1), round(
        (img1_shape[0] - img0_shape[0] * gain) / 2 - 0.1)
    boxes[..., [0, 2]] -= pad[0]
    boxes[..., [1, 3]] -= pad[1]
    boxes[..., :4] /= gain

    boxes[..., 0].clamp_(0, img0_shape[1])  # x1
    boxes[..., 1].clamp_(0, img0_shape[0])  # y1
    boxes[..., 2].clamp_(0, img0_shape[1])  # x2
    boxes[..., 3].clamp_(0, img0_shape[0])  # y2

    return boxes


def nms(pred: torch.Tensor, nms_arg: dict[int, float] | float = 0.25, iou_thres=0.45, max_det=1500):
    """
    非极大值抑制。

    Args:
        pred (torch.Tensor): 形状为(n, 6)或(b, n, 6)的边界框坐标和置信度。
        nms_arg (dict[int, float] | float, optional): 一个字典，用于指定每个类别的nms阈值。如果为float，则使用相同的阈值。默认为0.25。
        iou_thres (float, optional): 用于nms的iou阈值。默认为0.45。
        max_det (int, optional): 最多保留的检测框数量。默认为1500。

    Returns:
        torch.Tensor: 形状为(m, 6)的边界框坐标和置信度。
    """

    # 获取nms参数
    class_num = pred.shape[0] - 4  # 类别数量
    nms_arg = {i: nms_arg for i in range(class_num)} if isinstance(nms_arg, float) else nms_arg
    class_list = list(nms_arg.keys())
    conf_list = list(nms_arg.values())

    # 初始化条件
    condition = torch.zeros(pred.shape[1], dtype=torch.bool, device=pred.device)
    for classes, conf in zip(class_list, conf_list):
        condition = torch.logical_or(condition, pred[4 + classes, :] >= conf)
    pred = pred[:, condition]

    # 如果没有检测框，则返回空
    if not pred.shape[1]:
        return torch.zeros((0, 6), device=pred.device)

    # 将x,y,w,h转换为xyxy
    pred = pred.transpose(1, 0)
    pred[..., :4] = xywh2xyxy(pred[..., :4])

    # 将每个类别的检测框和置信度拼接成一个数组
    box, cls = pred.split((4, class_num), 1)
    conf, j = cls.max(1, keepdim=True)
    pred = torch.cat((box, conf, j.float()), 1)

    # 筛选需要检测的类别
    if len(class_list) != class_num:
        pred = pred[(pred[:, 5:6] == torch.tensor(class_list, device=pred.device)).any(1)]

    # 如果没有检测框，则返回空
    if not pred.shape[0]:
        return torch.zeros((0, 6), device=pred.device)

    # 进行nms计算
    c = pred[:, 5:6] * 7680
    boxes, scores = pred[:, :4] + c, pred[:, 4]
    index = torchvision.ops.nms(boxes, scores, iou_thres)
    index = index[:max_det]

    return pred[index]


def xyxy2xywh(x):
    """
    将边界框坐标从（x1，y1，x2，y2）格式转换为（x，y，w，h）格式，其中（x1，y1）为左上角，（x2，y2）为右下角。

    Args:
    x（np.ndarray | torch.Tensor）：（x1，y1，x2，y2）格式的输入边界框坐标。

    Returns:
    y（np.ndarray | torch.Tensor）：（x，y，w，h）格式的边界框坐标。
    """

    y = torch.empty_like(x) if isinstance(x, torch.Tensor) else np.empty_like(x)  # faster than clone/copy
    y[..., 0] = (x[..., 0] + x[..., 2]) / 2  # x center
    y[..., 1] = (x[..., 1] + x[..., 3]) / 2  # y center
    y[..., 2] = x[..., 2] - x[..., 0]  # width
    y[..., 3] = x[..., 3] - x[..., 1]  # height
    return y


def xywh2xyxy(x):
    """
    将边界框坐标从（x，y，w，h）格式转换为（x1，y1，x2，y2）格式，其中（x1，y1）是左上角，（x2，y2）是右下角。

    Args:
    x（np.ndarray | torch.Tensor）：（x，y，w，h）格式的输入边界框坐标。

    Returns:
    y（np.ndarray | torch.Tensor）：（x1，y1，x2，y2）格式的边界框坐标。
    """

    y = torch.empty_like(x) if isinstance(x, torch.Tensor) else np.empty_like(x)
    dw = x[..., 2] / 2  # half-width
    dh = x[..., 3] / 2  # half-height
    y[..., 0] = x[..., 0] - dw  # top left x
    y[..., 1] = x[..., 1] - dh  # top left y
    y[..., 2] = x[..., 0] + dw  # bottom right x
    y[..., 3] = x[..., 1] + dh  # bottom right y
    return y


def xywhr2xyxyxyxy(rboxes):
    """将带有角度的矩形框转换为四个顶点坐标,xywhr格式为(x,y,w,h,r),r为角度，单位为弧度。xyxyxyxy格式为(x1,y1,x2,y2,x3,y3,x4,y4)"""

    is_numpy = isinstance(rboxes, np.ndarray)
    cos, sin = (np.cos, np.sin) if is_numpy else (torch.cos, torch.sin)

    ctr = rboxes[..., :2]
    w, h, angle = (rboxes[..., i: i + 1] for i in range(2, 5))
    cos_value, sin_value = cos(angle), sin(angle)
    vec1 = [w / 2 * cos_value, w / 2 * sin_value]
    vec2 = [-h / 2 * sin_value, h / 2 * cos_value]
    vec1 = np.concatenate(vec1, axis=-1) if is_numpy else torch.cat(vec1, dim=-1)
    vec2 = np.concatenate(vec2, axis=-1) if is_numpy else torch.cat(vec2, dim=-1)
    pt1 = ctr + vec1 + vec2
    pt2 = ctr + vec1 - vec2
    pt3 = ctr - vec1 - vec2
    pt4 = ctr - vec1 + vec2

    if is_numpy:
        return np.concatenate([pt1, pt2, pt3, pt4], axis=-1)
    else:
        return torch.cat([pt1, pt2, pt3, pt4], dim=-1)


def xyxy2xyxyxyxy(boxes):
    """将边界框坐标从(x1,y1,x2,y2)格式转换为(x1,y1,x2,y2,x3,y3,x4,y4)格式,xyxy是左上角右下角坐标，xyxyxyxy是四个顶点坐标"""

    is_numpy = isinstance(boxes, np.ndarray)
    x1 = boxes[..., 0]
    y1 = boxes[..., 1]
    x2 = boxes[..., 2]
    y2 = boxes[..., 3]

    if is_numpy:
        vertices = np.concatenate((
            np.stack((x1, y1), axis=-1),
            np.stack((x2, y1), axis=-1),
            np.stack((x2, y2), axis=-1),
            np.stack((x1, y2), axis=-1)
        ), axis=-1)
    else:
        vertices = torch.cat((
            torch.stack((x1, y1), dim=-1),
            torch.stack((x2, y1), dim=-1),
            torch.stack((x2, y2), dim=-1),
            torch.stack((x1, y2), dim=-1)
        ), dim=-1)

    return vertices


def is_point_inside_polygon(x: int, y: int, polygon: np.ndarray):
    """
    判断点是否在多边形内
    """

    n = len(polygon)
    inside = False

    for i in range(n):
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]

        # 使用射线交点法判断点是否在多边形内部
        if ((y1 <= y < y2) or (y2 <= y < y1)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
            inside = not inside

    return inside


def point_to_curve_distance(point, func):
    """
    计算点到曲线的距离
    Args:
    point: 点坐标
    func: 曲线函数

    Returns:
    点到曲线的距离
    """

    x0, y0 = point
    initial_guess = np.asarray((x0))
    def optimized_func(x): return ((func(x) - y0) ** 2 + (x - x0) ** 2) ** 0.5
    result = optimize.minimize(optimized_func, initial_guess, method='COBYLA')

    distance = result.fun

    return distance


def fit_curve(points: list, degree=3):
    """
    根据点集拟合曲线
    Args:
    points: 点集, 格式为[(x1, y1), (x2, y2), ...]
    degree: 曲线阶数

    Returns:
    曲线函数
    """

    if len(points) == 0:
        return None

    points = np.array(points)
    coefficients = np.polyfit(points[:, 0], points[:, 1], degree)
    func = np.poly1d(coefficients)

    return func


# TODO 临时函数，待优化
def xywhr2x1y1x2y2(rbox):
    rect = ((rbox[0], rbox[1]), (rbox[2], rbox[3]), rbox[4] * 180 / np.pi)  # 构造旋转矩形(rect)
    box_points = cv2.boxPoints(rect)  # 获取旋转矩形的四个顶点坐标
    x1, y1 = np.int0(np.min(box_points, axis=0))
    x2, y2 = np.int0(np.max(box_points, axis=0))

    return x1, y1, x2, y2


# TODO 待优化
def _xywhr2x1y1x2y2(rboxes: np.ndarray | list | tuple):
    if isinstance(rboxes, np.ndarray):
        return np.apply_along_axis(xywhr2x1y1x2y2, axis=1, arr=rboxes)
    elif isinstance(rboxes, (list, tuple)):
        return [_xywhr2x1y1x2y2(rbox) for rbox in rboxes]
    else:
        raise TypeError('rboxes must be numpy.ndarray or list or tuple')
