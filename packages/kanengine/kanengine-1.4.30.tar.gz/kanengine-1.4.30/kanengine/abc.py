"""算法抽象类"""

from abc import ABC, abstractmethod


class EngineABC(ABC):

    @abstractmethod
    def _preprocess(self, *args, **kwargs):
        """前处理"""

    @abstractmethod
    def _infer(self, *args, **kwargs):
        """推理"""

    @abstractmethod
    def _postprocess(self, *args, **kwargs):
        """后处理"""

    def _warmup(self, *args, **kwargs):
        """预热"""


class CombineEngineABC(ABC):
    pass
