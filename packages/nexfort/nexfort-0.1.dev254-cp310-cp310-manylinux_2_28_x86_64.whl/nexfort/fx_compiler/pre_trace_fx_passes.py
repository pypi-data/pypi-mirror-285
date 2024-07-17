from typing import List

import torch

from nexfort.fx_compiler import config as fx_config
from nexfort.utils.logging import logger


def apply_fx_passes(gm: torch.fx.GraphModule, example_inputs: List[torch.Tensor]) -> torch.fx.GraphModule:
    pre_aot_config = fx_config.pre_aot

    if pre_aot_config.disable:
        logger.debug("Skipping all pre_trace passes because it is disabled")
        return gm

    return gm
