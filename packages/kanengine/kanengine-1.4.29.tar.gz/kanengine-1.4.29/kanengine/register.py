"""注册器"""


class Register(object):

    def __init__(self) -> None:
        self._module_dict = {}
        self._instance_dict = {}

    def register(self, name=''):
        def inner(cls_or_func):
            key = name if name else cls_or_func.__name__
            self._module_dict.setdefault(key, cls_or_func)
            return cls_or_func

        return inner

    def run(self, engine_name: str, *, params: dict, model_name: str):
        obj = self(engine_name)(**params)
        self._instance_dict.setdefault(model_name, obj)

        return obj

    def __call__(self, engine_name: str):
        cls_or_func = self._module_dict.get(engine_name)
        if cls_or_func is None:
            raise KeyError(f'Class or Function {engine_name} not found in registry!')

        return cls_or_func

    def get(self, model_name: str):
        return self._instance_dict.get(model_name)

    def __repr__(self) -> str:
        string = self.__class__.__name__ + ':' + str(list(self._module_dict.keys()))
        return string


ENGINES = Register()
