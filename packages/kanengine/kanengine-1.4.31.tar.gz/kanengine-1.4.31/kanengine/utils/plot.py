import cv2
import numpy as np

palette = [
    (115, 43, 245), (255, 115, 100), (52, 69, 147), (0, 194, 255), (0, 24, 236),
    (132, 56, 255), (82, 0, 133), (203, 56, 255), (255, 149, 200), (255, 55, 199),
    (64, 125, 255), (255, 112, 31), (255, 178, 29), (207, 210, 49), (214, 112, 218),
    (72, 249, 10), (146, 204, 23), (61, 219, 134), (26, 147, 52), (0, 212, 187)
]


def choose_color(index: int):
    return palette[index % len(palette)]


def plot_box(
        image: np.ndarray, box: list | np.ndarray,
        label='', color=(128, 128, 128),
        line_width=2, text_thickness=1,
        box_format='xyxy', return_pts=False
):
    """
    根据矩形框的格式(xyxy、xywh、xywha)，绘制矩形框(水平矩形框或旋转矩形框)。
    Args:
        image: 图像
        box: 矩形框坐标，格式为(x1, y1, x2, y2)或(x, y, w, h)或(x, y, w, h, angle)或(x1, y1, x2, y2, x3, y3, x4, y4)
        label: 标签名称
        color: 矩形框颜色
        line_width: 矩形框线宽
        text_thickness: 标签文字的粗细
        box_format: 矩形框格式, 可选'xyxy'、'xywh'、'xywha'、'xyxyxyxy', 默认'xyxy'
        return_pts: 是否返回矩形框的四个顶点坐标，格式为(x1, y1, x2, y2, x3, y3, x4, y4),形状为(8,)
    Returns:
        绘制后的图像或(图像, 矩形框四个顶点坐标)
    """

    args = image, box, label, color, line_width, text_thickness, return_pts
    if box_format == 'xyxyxyxy':
        return plot_box_by_xyxyxyxy(*args)
    elif box_format == 'xyxy':
        return plot_box_by_xyxy(*args)
    elif box_format == 'xywh':
        return plot_box_by_xywh(*args)
    elif box_format == 'xywha':
        return plot_box_by_xywha(*args)
    else:
        raise ValueError(f'Unsupported box format: {box_format}')


def plot_box_by_xyxyxyxy(
        image: np.ndarray, box: list | np.ndarray,
        label='', color=(128, 128, 128),
        line_width=2, text_thickness=1, return_pts=False
):
    """根据四个顶点坐标绘制矩形框。"""

    box = np.asarray(box, dtype=np.int32).reshape((-1, 2))
    cv2.polylines(image, [box], True, color, line_width)

    if label:
        cv2.putText(
            img=image,
            text=label,
            org=tuple(box[0]),
            fontFace=3,
            fontScale=0.95,
            color=color,
            thickness=text_thickness,
            lineType=cv2.LINE_AA
        )

    return (image, box.reshape(-1)) if return_pts else image


def plot_box_by_xyxy(
        image: np.ndarray, box: list | np.ndarray,
        label='', color=(128, 128, 128),
        line_width=2, text_thickness=1, return_pts=False
):
    """根据矩形框的左上角和右下角坐标绘制水平矩形框。若return_pts为True，则返回图像和矩形框的四个顶点坐标"""

    p1, p2 = (int(box[0]), int(box[1])), (int(box[2]), int(box[3]))
    cv2.rectangle(image, p1, p2, color, thickness=line_width, lineType=cv2.LINE_AA)

    if label:
        cv2.putText(
            img=image,
            text=label,
            org=(p1[0], p1[1] - 2 * line_width),
            fontFace=3,
            fontScale=0.95,
            color=color,
            thickness=text_thickness,
            lineType=cv2.LINE_AA
        )

    box = np.array([p1[0], p1[1], p2[0], p1[1], p2[0], p2[1], p1[0], p2[1]], dtype=np.int32)

    return (image, box) if return_pts else image


def plot_box_by_xywh(
        image: np.ndarray, box: list | np.ndarray,
        label='', color=(128, 128, 128),
        line_width=2, text_thickness=1, return_pts=False
):
    """根据矩形框的中心点坐标和宽高绘制水平矩形框。若return_pts为True，则返回图像和矩形框的四个顶点坐标。"""

    x, y, w, h = box
    box = [x - w / 2, y - h / 2, x + w / 2, y + h / 2]
    return plot_box_by_xyxy(image, box, label, color, line_width, text_thickness, return_pts)


def plot_box_by_xywha(
        image: np.ndarray, box: list | np.ndarray,
        label='', color=(128, 128, 128),
        line_width=2, text_thickness=1, return_pts=False
):
    """根据矩形框的中心点坐标、宽高和旋转角度绘制旋转矩形框。若return_pts为True，则返回图像和矩形框的四个顶点坐标。"""

    x, y, w, h, angle = box
    angle = np.rad2deg(angle)
    box = cv2.boxPoints(((x, y), (w, h), angle))
    box = box.astype(np.int32)

    cv2.polylines(image, [box], True, color, line_width)

    if label:
        cv2.putText(
            img=image,
            text=label,
            org=tuple(box[0]),
            fontFace=3,
            fontScale=0.95,
            color=color,
            thickness=text_thickness,
            lineType=cv2.LINE_AA
        )

    return (image, box.reshape(-1)) if return_pts else image


def plot_dot(image: np.ndarray, point: tuple, *, color=(0, 255, 50), radius=3):
    """绘制一个点"""

    cv2.circle(image, point, radius, color, -1)

    return image


def plot_dots(image: np.ndarray, points: np.ndarray, *, color=(0, 255, 50), radius=3):
    """绘制多个点"""

    for point in points:
        cv2.circle(image, (point[0], point[1]), radius, color, -1)

    return image


def plot_box_from_rbox(
        image: np.ndarray, rbox: np.ndarray, label=None,
        color=(128, 128, 128), line_width=2, return_pts=False
):
    """根据旋转矩形框坐标绘制水平矩形框。若return_pts为True，则返回矩形框的四个顶点坐标。"""

    rect = ((rbox[0], rbox[1]), (rbox[2], rbox[3]), rbox[4] * 180 / np.pi)  # 构造旋转矩形(rect)
    box_points = cv2.boxPoints(rect)  # 获取旋转矩形的四个顶点坐标
    x1, y1 = np.int0(np.min(box_points, axis=0))
    x2, y2 = np.int0(np.max(box_points, axis=0))
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)  # 绘制矩形框

    if label:
        cv2.putText(
            img=image,
            text=label,
            org=(x1, y1 - 2 * line_width),
            fontFace=3,
            fontScale=0.95,
            color=color,
            thickness=1,
            lineType=cv2.LINE_AA
        )

    if return_pts:
        return image, (x1, y1, x2, y2)

    return image
