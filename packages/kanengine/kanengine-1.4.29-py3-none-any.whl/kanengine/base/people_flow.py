"""人流量检测模块"""

import torch
import numpy as np
import cv2

from torchvision import transforms

from ..abc import EngineABC

img_transform = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
tensor_transform = transforms.ToTensor()


class BasePeopleFlowDetect(EngineABC):

    def __init__(self, weight_path: str, **kwargs) -> None:
        import onnxruntime as rt

        self.model = rt.InferenceSession(weight_path, providers=['CUDAExecutionProvider'])
        self._warmup()

    def _warmup(self):
        """预热"""
        for _ in range(2):
            arr = np.random.randn(12, 3, 256, 256).astype(np.float32)
            self.model.run(None, {'samples': arr})

    def __call__(self, orig_img, threshold=0.30):
        """检测,流程为:前处理 --> 推理 --> 后处理

        Parameters
        ----------
        orig_img :
            原始图像列表
        threshold :
            判断人或背景的置信度的阈值

        Returns
        -------
        np.ndarray
            返回每张图像中人的坐标
        """
        tensor_im, scale_h, scale_w = self._preprocess(orig_img)

        tensor_im = tensor_im.detach().numpy()

        preds = self._infer(tensor_im)

        args = scale_h, scale_w
        processed_pred = self._postprocess(preds, threshold, *args)
        return processed_pred

    def _infer(self, image: np.ndarray):
        """推理"""
        return self.model.run(None, {'samples': image})

    def _preprocess(self, image: np.ndarray):
        """前处理

        Parameters
        ----------
        image :  np.ndarray
            原始图像

        Returns
        -------
        torch.Tensor
            返回预处理结果
        """

        width = 1024
        height = 768

        scale_w = image.shape[1] / 1024
        scale_h = image.shape[0] / 768
        image = cv2.resize(image, (width, height), interpolation=cv2.INTER_NEAREST)
        image = tensor_transform(image)
        image = img_transform(image)
        num_w = 4
        num_h = 3
        image = image.view(3, num_h, 256, 1024).view(3, num_h, 256, num_w, 256)
        image = image.permute(0, 1, 3, 2, 4).contiguous().view(3, num_w * num_h, 256, 256).permute(1, 0, 2, 3)

        return image, scale_h, scale_w

    def _postprocess(self, outputs: list, threshold: float, *args):
        """后处理一批图像的推理结果

        Parameters
        ----------
        outputs: list
            模型推理的结果
        threshold : float
            调整阈值
        args
            其他参数
        """
        num_w = 4
        num_h = 3
        scale_h, scale_w = args
        out_logits, out_point = torch.from_numpy(outputs[0]), torch.from_numpy(outputs[1])

        prob = out_logits.sigmoid()
        topk_values, topk_indexes = torch.topk(prob.view(out_logits.shape[0], -1), 700, dim=1)

        topk_points = topk_indexes // out_logits.shape[2]
        out_point = torch.gather(out_point, 1, topk_points.unsqueeze(-1).repeat(1, 1, 2))
        out_point = out_point * 256

        value_points = torch.cat([topk_values.unsqueeze(2), out_point], 2)
        crop_size = 256

        kpoint_list = []

        for i in range(len(value_points)):
            out_value = value_points[i][:, 0].data.cpu().numpy()
            out_point = value_points[i][:, 1:3].data.cpu().numpy().astype(int)
            k = np.zeros((crop_size, crop_size))

            '''get coordinate'''
            for j in range(700):
                if out_value[j] < threshold:
                    break
                x = out_point[j, 0]
                y = out_point[j, 1]
                k[x, y] = 1
            kpoint_list.append(k)

        kpoint = torch.from_numpy(np.array(kpoint_list)).unsqueeze(0)
        kpoint = (
            kpoint.view(num_h, num_w, crop_size, crop_size)
            .permute(0, 2, 1, 3)
            .contiguous()
            .view(num_h, crop_size, 1024)
            .view(768, 1024)
            .cpu()
            .numpy()
        )

        '''obtain the coordinate '''
        pred_coor = np.nonzero(kpoint)
        x = pred_coor[1] * scale_w
        y = pred_coor[0] * scale_h

        return np.stack((x, y), axis=1)
