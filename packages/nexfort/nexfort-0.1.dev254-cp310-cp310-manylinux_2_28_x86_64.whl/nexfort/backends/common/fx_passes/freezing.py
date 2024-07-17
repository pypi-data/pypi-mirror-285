from typing import List

import torch

from nexfort.utils import checks
from nexfort.utils.logging import logger


# Freezing parameters that are not mutated into constants and optimizes the graph through constant propagation.
# This is torch Inductor's freezing.
def fx_pass_freeze(gm: torch.fx.GraphModule, example_inputs: List[torch.Tensor]) -> torch.fx.GraphModule:
    if not checks.is_inductor_supported():
        logger.warning("Inductor is not supported. Skip freezing.")
        return gm

    from torch._guards import tracing
    from torch._inductor.freezing import freeze

    """
    Inlines parameters that are not mutated into constants and optimizes the graph through constant propagation
    and other techniques. If enabled, the function also discards the original parameters of the module for memory efficiency.

    Assumes that this function is run in dynamo tracing post aot_autograd.

    Args:
        dynamo_gm (torch.fx.GraphModule): The Dynamo constructed GraphModule.
        aot_autograd_gm (torch.fx.GraphModule): The aot_autograd constructed GraphModule to be frozen.
        example_inputs (List[torch.Tensor]): A list of example input tensors to be used in the freezing process.

    Returns:
        Tuple[torch.fx.GraphModule, List[int]]: A tuple containing the frozen GraphModule and a list of indices
        of the inputs that were preserved (not turned into constants).
    """

    with tracing(None):
        gm = freeze(None, gm, example_inputs)[0]

    return gm
