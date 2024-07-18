"""模型导出"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path

from loguru import logger as LOGGER


def expoort_in_subprocess(**kwargs):
    """在子进程中运行模型导出脚本"""

    arg_list = []
    for k, v in kwargs.items():
        if isinstance(v, bool):
            arg_list.append(f'--{k}' if v else '')
        elif isinstance(v, (list, tuple)):
            arg_list.append(f'--{k}={str(v).replace(" ","")}')
        else:
            arg_list.append(f'--{k}={v}')

    cmds = [sys.executable, __file__] + list(filter(lambda x: x, arg_list))
    LOGGER.info(f"开始执行转换命令: {' '.join(cmds)}")

    # 使用subprocess.Popen启动子进程，设置缓冲区大小为1，表示行缓冲
    process = subprocess.Popen(
        cmds,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True
    )

    while True:
        output = process.stdout.readline()
        # 如果output为空字符串且process已经结束，跳出循环
        if output == '' and process.poll() is not None:
            break
        if output:
            LOGGER.debug(output.strip())

    # 等待子进程结束并获取返回码
    rc = process.poll()
    return rc


def export_engine(
        f_onnx: str,  dynamic=False,
        half=False, input_shape=(1, 3, 640, 640),
        workspace=4, engine_file=None,
        prefix='TensorRT:'
):
    """
    将ONNX模型导出为TensorRT engine文件
    Args:
        f_onnx: str, ONNX模型文件路径
        prefix: str, 日志前缀
        workspace: int, 工作空间大小(MB)
        dynamic: bool, 是否为动态输入
        half: bool, 是否使用半精度浮点数
        input_shape: tuple, 输入尺寸
        engine_file: str, 导出engine文件路径

    Returns:
        f_engine: str, 导出engine文件路径
    """

    import tensorrt as trt

    t_start = time.time()
    LOGGER.info(f"{prefix} 开始导出模型,TensorRT版本:{trt.__version__},PID:{os.getpid()}")
    f_engine = engine_file or f_onnx.replace('.onnx', '.engine')

    # 创建builder和network
    logger = trt.Logger(trt.Logger.INFO)
    builder = trt.Builder(logger)
    config = builder.create_builder_config()
    config.max_workspace_size = workspace * 1 << 30
    flag = 1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
    network = builder.create_network(flag)

    # 解析ONNX文件
    parser = trt.OnnxParser(network, logger)
    if not parser.parse_from_file(f_onnx):
        raise RuntimeError(f"加载onnx文件失败:{Path(f_onnx).absolute()}")

    # 构建engine
    inputs = [network.get_input(i) for i in range(network.num_inputs)]
    outputs = [network.get_output(i) for i in range(network.num_outputs)]
    for inp in inputs:
        LOGGER.info(f'{prefix} input "{inp.name}" with shape{inp.shape} {inp.dtype}')
    for out in outputs:
        LOGGER.info(f'{prefix} output "{out.name}" with shape{out.shape} {out.dtype}')

    # 处理动态输入
    if dynamic:
        shape = input_shape
        profile = builder.create_optimization_profile()
        for inp in inputs:
            profile.set_shape(inp.name, (1, *shape[1:]), (max(1, shape[0] // 2), *shape[1:]), shape)
        config.add_optimization_profile(profile)

    # 设置精度
    LOGGER.info(
        f"{prefix} building FP{16 if builder.platform_has_fast_fp16 and  half else 32} engine as {f_engine}"
    )
    if builder.platform_has_fast_fp16 and half:
        config.set_flag(trt.BuilderFlag.FP16)

    # 序列化并持久化engine
    with builder.build_engine(network, config) as engine, open(f_engine, "wb") as t:
        LOGGER.info(f"{prefix} engine saved to {f_engine}")
        t.write(engine.serialize())

    t_end = time.time()
    LOGGER.info(f"{prefix} 导出模型完成,耗时:{t_end - t_start:.2f}秒")
    return f_engine


def main():
    parser = argparse.ArgumentParser(description='Export model')
    parser.add_argument('--f_onnx', type=str, required=True, help='onnx model file')
    parser.add_argument('--dynamic', action='store_true', help='dynamic input')
    parser.add_argument('--half', action='store_true', help='use half precision float')
    parser.add_argument('--input_shape', type=str, default='(1,3,640,640)', help='input shape')
    parser.add_argument('--workspace', type=int, default=4, help='workspace size(MB)')
    parser.add_argument('--engine_file', type=str, default=None, help='engine file path')
    parser.add_argument('--prefix', type=str, default='TensorRT:', help='log prefix')
    args = parser.parse_args()

    input_shape = tuple(map(int, args.input_shape[1:-1].split(',')))

    args.__dict__['input_shape'] = input_shape
    LOGGER.info(f"参数:{args.__dict__}")
    export_engine(**args.__dict__)


if __name__ == '__main__':
    main()
