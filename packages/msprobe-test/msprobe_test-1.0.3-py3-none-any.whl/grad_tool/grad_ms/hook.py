from functools import wraps
import os
import shutil

import mindspore
import mindspore as ms
from mindspore.common.api import jit
from mindspore.nn.optim.optimizer import Optimizer
from mindspore.common.parameter import Parameter
from mindspore.common.initializer import initializer

from grad_tool.common.constant import GradConst
from grad_tool.common.utils import print_warn_log
from grad_tool.grad_ms.global_context import grad_context
from grad_tool.grad_ms.grad_analyzer import grad_dump, get_rank_id
from grad_tool.grad_ms.grad_analyzer import csv_generator


def hook_optimizer(opt: Optimizer):
    func = opt.construct
    g_names = [param.name for param in opt._parameters]
    param_list = grad_context.get_context(GradConst.PARAM_LIST)
    rank_id = get_rank_id()
    output_path = grad_context.get_context(GradConst.OUTPUT_PATH)
    dump_dir = f"{output_path}/rank_{rank_id}/Dump/"
    save_dir = f"{output_path}/rank_{rank_id}/"
    step_finish_flag = f"{output_path}/rank_{rank_id}/Dump/{GradConst.STEP_FINISH}"
    if os.path.exists(save_dir):
        print_warn_log(f"Delete existing path {save_dir}.")
        shutil.rmtree(save_dir)
    level = grad_context.get_context(GradConst.LEVEL)
    bounds = grad_context.get_context(GradConst.BOUNDS)

    @jit
    def new_construct(self, gradients):
        for index, grad_value in enumerate(gradients):
            if param_list and g_names[index] not in param_list:
                continue
            grad_dump(dump_dir, g_names[index], self.dump_step, grad_value, level, bounds)
        ms.ops.TensorDump()(step_finish_flag, self.dump_step)
        self.assignadd(self.dump_step, self.global_step_increase_tensor)
        out = func(gradients)
        return out

    opt.dump_step = Parameter(initializer(0, [1], ms.int32), name="dump_step")
    opt.construct = new_construct.__get__(opt, type(opt))
    csv_generator.start()
